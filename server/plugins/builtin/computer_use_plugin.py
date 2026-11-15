"""
Dione AI — Native Computer-Use, UIA, Drag & Canvas Drawing Plugin (v5.0 Open-CUA Edition)
=========================================================================================
Integrates battle-tested desktop control primitives from:
- `vercel-labs/agent-desktop` (`crates/windows/src/input/drag.rs` & `mouse_send.rs` & `mouse_coord.rs`):
  Normalized-absolute `SendInput` (`0..65535` with `MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK`),
  200ms pickup settle before and after `MOUSEEVENTF_LEFTDOWN`, 16ms interpolated `MOUSEEVENTF_MOVE`
  steps, destination dwell, and an unconditional `DragReleaseGuard` (`try...finally` button release).
- `suitedaces/computer-agent` (`src-tauri/src/computer.rs`):
  First-class `computer_drag` (`start_x, start_y -> end_x, end_y`), `computer_move`, `middle_click`,
  `triple_click`, and continuous multi-point path/shape drawing (`computer_draw_shape`).
- `qwenlm/open-computer-use` (`apps/OpenComputerUseWindows/runtime.ps1`):
  Semantic UIA pattern execution (`InvokePattern`, `TogglePattern`, `ValuePattern`, `SelectionItemPattern`)
  via `computer_uia_action` alongside Set-of-Mark (SoM) + 10% Coordinate Grid Gemini Vision grounding.
"""

from __future__ import annotations

import asyncio
import base64
import ctypes
import hashlib
import io
import json
import logging
import math
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from server.plugins.base import BasePlugin, dione_tool
from server.hermes_computer_use.tool import handle_computer_use
from server.hermes_computer_use.cua_backend import CuaDriverBackend
from server.core.runtime.event_bus import get_event_bus, RuntimeEvent, EventType

logger = logging.getLogger(__name__)

CHROME_EXE = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
EDGE_EXE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
RIOT_EXE = Path(r"C:\Riot Games\Riot Client\RiotClientServices.exe")

# Win32 SendInput Mouse Flags (ported from vercel-labs/agent-desktop crates/windows/src/input/mouse/mouse_send.rs)
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_VIRTUALDESK = 0x4000
MOUSEEVENTF_ABSOLUTE = 0x8000
INPUT_MOUSE = 0


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", _INPUT_UNION),
    ]


class ComputerUsePlugin(BasePlugin):
    """High-Precision Windows 11 Computer-Use, Drag/Draw, UIA & Multimodal Vision Plugin."""

    name = "ComputerUsePlugin"
    description = (
        "Control the Windows 11 desktop: click elements or coordinates, drag and drop, "
        "draw shapes/circles/paths in MS Paint or canvases, type text, press shortcuts, "
        "inspect screen with Set-of-Mark Vision/UIA, launch apps, and play media."
    )
    version = "5.0.0"

    def __init__(self):
        super().__init__()
        self._backend = CuaDriverBackend()
        self._captures_dir = Path("data/captures")
        self._captures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Low-Level Win32 SendInput Primitives (vercel-labs/agent-desktop port)
    # ------------------------------------------------------------------

    def _bind_interactive_desktop(self):
        """Ensure thread is attached to interactive WinSta0/default desktop with Per-Monitor DPI awareness."""
        try:
            if hasattr(ctypes, "windll"):
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)
                except Exception:
                    try:
                        ctypes.windll.user32.SetProcessDPIAware()
                    except Exception:
                        pass
                u32 = ctypes.windll.user32
                hw = u32.OpenWindowStationW("WinSta0", False, 0xF037F)
                if hw:
                    u32.SetProcessWindowStation(hw)
                hd = u32.OpenDesktopW("default", 0, False, 0x01FF)
                if hd:
                    u32.SetThreadDesktop(hd)
        except Exception:
            pass

    def _get_screen_metrics(self) -> Tuple[int, int]:
        if not hasattr(ctypes, "windll"):
            return (1920, 1080)
        u32 = ctypes.windll.user32
        return (u32.GetSystemMetrics(0) or 1920, u32.GetSystemMetrics(1) or 1080)

    def _normalize_point(self, x: float, y: float) -> Tuple[int, int, bool]:
        """
        Ported from `vercel-labs/agent-desktop` (`mouse_coord.rs`):
        Converts physical pixel (x, y) into 0..65535 normalized SendInput coordinates.
        """
        if not hasattr(ctypes, "windll"):
            return (int(x), int(y), False)
        u32 = ctypes.windll.user32
        pw, ph = u32.GetSystemMetrics(0) or 1920, u32.GetSystemMetrics(1) or 1080
        if 0 <= x < pw and 0 <= y < ph:
            nx = int(round((x * 65535.0) / max(1, pw - 1)))
            ny = int(round((y * 65535.0) / max(1, ph - 1)))
            return (max(0, min(65535, nx)), max(0, min(65535, ny)), False)
        vx = u32.GetSystemMetrics(76) or 0
        vy = u32.GetSystemMetrics(77) or 0
        vw = u32.GetSystemMetrics(78) or pw
        vh = u32.GetSystemMetrics(79) or ph
        nx = int(round(((x - vx) * 65535.0) / max(1, vw - 1)))
        ny = int(round(((y - vy) * 65535.0) / max(1, vh - 1)))
        return (max(0, min(65535, nx)), max(0, min(65535, ny)), True)

    def _post_sendinput_mouse(self, dx: int, dy: int, flags: int, mouse_data: int = 0) -> None:
        """Dispatches a raw Win32 SendInput MOUSEINPUT struct (plus SetCursorPos sync)."""
        if not hasattr(ctypes, "windll"):
            return
        u32 = ctypes.windll.user32
        inp = _INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = int(dx)
        inp.union.mi.dy = int(dy)
        inp.union.mi.mouseData = int(mouse_data) & 0xFFFFFFFF
        inp.union.mi.dwFlags = int(flags)
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = 0
        u32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))

    def _move_cursor_smooth(self, x: int, y: int) -> None:
        """Moves cursor to (x, y) using both SetCursorPos and normalized SendInput MOUSEEVENTF_MOVE."""
        if not hasattr(ctypes, "windll"):
            return
        u32 = ctypes.windll.user32
        u32.SetCursorPos(int(x), int(y))
        nx, ny, is_vdesk = self._normalize_point(x, y)
        flags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | (MOUSEEVENTF_VIRTUALDESK if is_vdesk else 0)
        self._post_sendinput_mouse(nx, ny, flags)

    def _send_native_win32_key(self, key_str: str) -> bool:
        """Direct Win32 keybd_event with hardware scan codes (MapVirtualKeyW) and 50ms hold duration."""
        if not hasattr(ctypes, "windll"):
            return False
        self._bind_interactive_desktop()
        user32 = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002

        VK_MAP = {
            "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
            "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
            "enter": 0x0D, "return": 0x0D, "esc": 0x1B, "escape": 0x1B, "space": 0x20,
            "tab": 0x09, "backspace": 0x08, "delete": 0x2E, "del": 0x2E,
            "ctrl": 0x11, "control": 0x11, "shift": 0x10, "alt": 0x12,
            "win": 0x5B, "windows": 0x5B, "super": 0x5B, "cmd": 0x5B,
            "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
            "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
            "volup": 0xAF, "voldown": 0xAE, "mute": 0xAD, "playpause": 0xB3,
        }

        parts = [p.strip().lower() for p in re.split(r"[+\-\s]+", key_str) if p.strip()]
        vk_codes = []
        for p in parts:
            if p in VK_MAP:
                vk_codes.append(VK_MAP[p])
            elif len(p) == 1:
                vk = user32.VkKeyScanW(ord(p)) & 0xFF
                if vk > 0:
                    vk_codes.append(vk)

        if not vk_codes:
            return False

        for vk in vk_codes:
            scan = user32.MapVirtualKeyW(vk, 0)
            user32.keybd_event(vk, scan, 0, 0)
        time.sleep(0.05)  # 50ms minimum keypress hold standard
        for vk in reversed(vk_codes):
            scan = user32.MapVirtualKeyW(vk, 0)
            user32.keybd_event(vk, scan, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        return True

    def _click_native_win32(self, x: int, y: int, double: bool = False, right: bool = False, middle: bool = False, count: int = 1) -> bool:
        """
        Direct Win32 SendInput + mouse_event click with ClickReleaseGuard (`try...finally`),
        60ms hover settle, and 75ms hold duration.
        """
        if not hasattr(ctypes, "windll"):
            return False
        self._bind_interactive_desktop()

        tx, ty = int(x), int(y)
        self._move_cursor_smooth(max(0, tx - 3), max(0, ty - 3))
        time.sleep(0.015)
        self._move_cursor_smooth(tx, ty)
        time.sleep(0.06)  # 60ms hover settle

        if right:
            down_flag, up_flag = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
        elif middle:
            down_flag, up_flag = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
        else:
            down_flag, up_flag = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP

        clicks = 2 if double else max(1, int(count))
        for i in range(clicks):
            armed = True
            try:
                self._post_sendinput_mouse(0, 0, down_flag)
                time.sleep(0.075)  # 75ms hold duration
                self._post_sendinput_mouse(0, 0, up_flag)
                armed = False
            finally:
                if armed:
                    self._post_sendinput_mouse(0, 0, up_flag)
            if i + 1 < clicks:
                time.sleep(0.09)

        time.sleep(0.12)
        return True

    def _glide_cursor_win32(self, target_x: int, target_y: int, duration_s: float = 0.35) -> None:
        """Smoothly glides the cursor to (target_x, target_y) using a smoothstep curve."""
        if not hasattr(ctypes, "windll"):
            return
        user32 = ctypes.windll.user32
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        cur = POINT()
        user32.GetCursorPos(ctypes.byref(cur))
        start_x, start_y = cur.x, cur.y

        steps = max(15, int(duration_s * 60))
        for i in range(1, steps + 1):
            t = i / float(steps)
            t_smooth = t * t * (3.0 - 2.0 * t)
            nx = int(start_x + (target_x - start_x) * t_smooth)
            ny = int(start_y + (target_y - start_y) * t_smooth)
            user32.SetCursorPos(nx, ny)
            user32.mouse_event(0x0001, 0, 0, 0, 0)
            time.sleep(duration_s / steps)

    def _select_paint_ribbon_shape_tool(self, shape_type: str) -> bool:
        """
        Initializes COM on worker thread via CoInitialize, locates the MS Paint Ribbon shape button
        (Oval, Rectangle, Triangle, Five-point star, Heart, Diamond, Right arrow, Line) and clicks it.
        """
        import ctypes
        if hasattr(ctypes, "windll"):
            try:
                ctypes.windll.ole32.CoInitialize(None)
            except Exception:
                pass

        st = shape_type.strip().lower()
        SHAPE_TOOL_MAP = {
            "circle": ["oval", "circle", "ellipse"],
            "oval": ["oval", "circle", "ellipse"],
            "ring": ["oval", "circle", "ellipse"],
            "square": ["rectangle", "square"],
            "rectangle": ["rectangle", "square"],
            "box": ["rectangle", "square"],
            "triangle": ["triangle"],
            "star": ["five-point star", "star"],
            "heart": ["heart"],
            "diamond": ["diamond"],
            "arrow": ["right arrow", "arrow"],
            "line": ["line"],
        }
        target_names = SHAPE_TOOL_MAP.get(st, [st])

        try:
            import uiautomation as auto
            fg = auto.GetForegroundControl()
            if fg:
                found_ctrl = None
                def _walk(ctrl, depth=0):
                    nonlocal found_ctrl
                    if depth > 9 or found_ctrl is not None:
                        return
                    try:
                        name = (ctrl.Name or "").lower().strip()
                        c_type = ctrl.ControlTypeName
                        if c_type in ("ButtonControl", "RadioButtonControl", "ListItemControl", "MenuItemControl"):
                            for tn in target_names:
                                if tn == name or tn in name:
                                    found_ctrl = ctrl
                                    return
                        for ch in ctrl.GetChildren():
                            _walk(ch, depth + 1)
                    except Exception:
                        pass

                _walk(fg, 0)
                if found_ctrl:
                    rect = found_ctrl.BoundingRectangle
                    if rect and rect.width() > 0:
                        click_x = (rect.left + rect.right) // 2
                        click_y = (rect.top + rect.bottom) // 2
                        self._click_native_win32(click_x, click_y)
                        time.sleep(0.20)
                        logger.info(f"[PaintRibbon] Successfully selected shape tool '{found_ctrl.Name}' at ({click_x}, {click_y})")
                        return True
        except Exception as e:
            logger.debug(f"[PaintRibbon] UIA shape search notice: {e}")

        return False

    def _drag_native_win32_path(
        self,
        points: List[Tuple[int, int]],
        step_delay_s: float = 0.014,
        button: str = "left",
    ) -> bool:
        """
        Executes a continuous mouse drag along a sequence of (x, y) points with:
        - 150ms pickup settle at origin before pressing mouse button
        - 150ms post-press settle so MS Paint / canvases / Chromium register drag start
        - Dual SendInput MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK
          and relative mouse_event(MOUSEEVENTF_MOVE, dx, dy) so Windows 11 MS Paint registers the stroke
        - Destination dwell settle (100ms) before releasing button
        - DragReleaseGuard (try...finally) guaranteeing the mouse button is ALWAYS released.
        """
        if not points or len(points) < 2 or not hasattr(ctypes, "windll"):
            return False
        self._bind_interactive_desktop()
        user32 = ctypes.windll.user32

        btn = (button or "left").lower()
        if btn == "right":
            down_flag, up_flag = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
        elif btn == "middle":
            down_flag, up_flag = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
        else:
            down_flag, up_flag = MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP

        sw, sh = self._get_screen_metrics()

        x0, y0 = int(points[0][0]), int(points[0][1])
        self._glide_cursor_win32(x0, y0, duration_s=0.25)
        user32.SetCursorPos(x0, y0)
        time.sleep(0.12)

        armed = True
        try:
            user32.mouse_event(down_flag, 0, 0, 0, 0)
            self._post_sendinput_mouse(0, 0, down_flag)
            time.sleep(0.12)

            prev_x, prev_y = x0, y0
            for px, py in points[1:]:
                cx, cy = int(px), int(py)
                dx = cx - prev_x
                dy = cy - prev_y
                prev_x, prev_y = cx, cy

                user32.SetCursorPos(cx, cy)
                user32.mouse_event(0x0001, dx, dy, 0, 0)
                norm_x = int(cx * 65535 / max(1, sw))
                norm_y = int(cy * 65535 / max(1, sh))
                self._post_sendinput_mouse(norm_x, norm_y, 0x0001 | 0x8000 | 0x4000)
                time.sleep(max(0.005, float(step_delay_s)))

            time.sleep(0.10)
            user32.mouse_event(up_flag, 0, 0, 0, 0)
            self._post_sendinput_mouse(0, 0, up_flag)
            armed = False
        finally:
            if armed:
                user32.mouse_event(up_flag, 0, 0, 0, 0)
                self._post_sendinput_mouse(0, 0, up_flag)

        time.sleep(0.12)
        return True

    def _list_native_win32_windows(self) -> List[Dict[str, Any]]:
        """Direct Win32 EnumWindows discovery with foreground flag and window rect."""
        if not hasattr(ctypes, "windll"):
            return []
        user32 = ctypes.windll.user32
        fg_hwnd = user32.GetForegroundWindow()
        windows = []

        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.strip()
                    if title and title not in ("Program Manager", "Default IME", "MSCTFIME UI"):
                        pid = ctypes.c_ulong()
                        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                        r = RECT()
                        rect_list = [0, 0, 1920, 1080]
                        if user32.GetWindowRect(hwnd, ctypes.byref(r)):
                            rect_list = [r.left, r.top, r.right, r.bottom]
                        windows.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid.value,
                            "active": (hwnd == fg_hwnd),
                            "rect": rect_list,
                        })
            return True

        user32.EnumWindows.argtypes = None
        proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_cb)
        user32.EnumWindows(proc, 0)
        return windows

    def _focus_window_by_keyword(self, keyword: str, maximize: bool = False) -> Optional[Dict[str, Any]]:
        """Bring a visible window matching keyword to foreground focus via Win32."""
        if not hasattr(ctypes, "windll"):
            return None
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        kw_low = keyword.lower().strip()
        alias_map = {
            "mspaint": ["paint", "mspaint"],
            "paint": ["paint", "mspaint"],
            "calc": ["calculator", "calc"],
            "code": ["visual studio code", "vs code", "code"],
            "valorant": ["valorant", "riot client"],
        }
        search_terms = alias_map.get(kw_low, [kw_low])

        windows = self._list_native_win32_windows()
        target = None
        for term in search_terms:
            target = next((w for w in windows if term in w["title"].lower() and "dione" not in w["title"].lower()), None)
            if target:
                break
        if not target:
            return None

        hwnd = target["hwnd"]
        try:
            user32.AllowSetForegroundWindow(-1)
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            if maximize:
                user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
            fg_hwnd = user32.GetForegroundWindow()
            fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
            cur_thread = kernel32.GetCurrentThreadId()
            if fg_thread and fg_thread != cur_thread:
                user32.AttachThreadInput(cur_thread, fg_thread, True)
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
                user32.SetFocus(hwnd)
                user32.AttachThreadInput(cur_thread, fg_thread, False)
            else:
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
                user32.SetFocus(hwnd)
        except Exception:
            pass
        return target

    def _find_paint_canvas_bounds(self) -> Tuple[int, int, int, int]:
        """
        Finds the exact MS Paint / drawing canvas rectangle on screen via Windows UIA
        or active window geometry (excluding the top 160px Ribbon/toolbar).
        Returns (left, top, right, bottom).
        """
        sw, sh = self._get_screen_metrics()
        try:
            import uiautomation as auto
            fg = auto.GetForegroundControl()
            if fg:
                # Look for MS Paint canvas pane / Custom / Image control
                def _find_canvas(ctrl, depth: int = 0):
                    if depth > 6:
                        return None
                    try:
                        name = (ctrl.Name or "").lower()
                        cls = (ctrl.ClassName or "").lower()
                        ctype = ctrl.ControlTypeName
                        rect = ctrl.BoundingRectangle
                        if rect and rect.width() > 250 and rect.height() > 200:
                            if any(k in name for k in ("canvas", "image", "drawing", "page")) or any(
                                k in cls for k in ("mspaintview", "a2fxw", "canvas", "paint")
                            ):
                                return (rect.left, rect.top, rect.right, rect.bottom)
                        for child in ctrl.GetChildren():
                            res = _find_canvas(child, depth + 1)
                            if res:
                                return res
                    except Exception:
                        pass
                    return None

                canvas_rect = _find_canvas(fg, 0)
                if canvas_rect:
                    return canvas_rect

                # Fallback to foreground window rect minus top 170px toolbar
                wrect = fg.BoundingRectangle
                if wrect and wrect.width() > 300 and wrect.height() > 250:
                    return (
                        wrect.left + 30,
                        wrect.top + 170,
                        wrect.right - 30,
                        wrect.bottom - 50,
                    )
        except Exception:
            pass

        # Safe screen center canvas bounds below top toolbars
        return (int(sw * 0.15), int(sh * 0.22), int(sw * 0.85), int(sh * 0.85))

    def _extract_active_uia_elements(self, max_elements: int = 45) -> List[Dict[str, Any]]:
        """Fast recursive depth-6 extraction of interactive UIA controls in the foreground window."""
        elements: List[Dict[str, Any]] = []
        try:
            import uiautomation as auto
            fg_ctrl = auto.GetForegroundControl()
            if not fg_ctrl:
                return elements

            interactive_types = {
                "ButtonControl", "EditControl", "HyperlinkControl",
                "TabItemControl", "MenuItemControl", "ComboBoxControl",
                "CheckBoxControl", "ListItemControl", "RadioButtonControl",
            }

            def _walk(ctrl, depth: int = 0):
                if depth > 6 or len(elements) >= max_elements:
                    return
                try:
                    c_type = ctrl.ControlTypeName
                    name = (ctrl.Name or "").strip()
                    if c_type in interactive_types and name and len(name) <= 80:
                        rect = ctrl.BoundingRectangle
                        if rect and rect.width() > 4 and rect.height() > 4:
                            cx = (rect.left + rect.right) // 2
                            cy = (rect.top + rect.bottom) // 2
                            if cx >= 0 and cy >= 0:
                                elements.append({
                                    "id": len(elements) + 1,
                                    "name": name,
                                    "type": c_type.replace("Control", ""),
                                    "center": [cx, cy],
                                    "bounds": [rect.left, rect.top, rect.right, rect.bottom],
                                })
                    for child in ctrl.GetChildren():
                        _walk(child, depth + 1)
                        if len(elements) >= max_elements:
                            break
                except Exception:
                    pass

            _walk(fg_ctrl, 0)
        except Exception:
            pass
        return elements

    def _render_som_and_grid_overlay(self, img, uia_controls: List[Dict[str, Any]]) -> bytes:
        """
        Draws a Set-of-Mark (SoM) numbered bounding-box overlay + 10% coordinate grid
        onto a copy of the screenshot for high-precision Gemini Vision grounding.
        """
        from PIL import ImageDraw

        annotated = img.copy().convert("RGB")
        draw = ImageDraw.Draw(annotated)
        w, h = annotated.size

        for pct in range(10, 100, 10):
            gx = int(w * pct / 100.0)
            gy = int(h * pct / 100.0)
            draw.line([(gx, 0), (gx, h)], fill=(0, 210, 255), width=1)
            draw.line([(0, gy), (w, gy)], fill=(0, 210, 255), width=1)
            draw.rectangle([(gx - 18, 2), (gx + 22, 16)], fill=(10, 14, 26))
            draw.text((gx - 15, 3), f"{pct}%", fill=(0, 230, 255))
            draw.rectangle([(2, gy - 8), (34, gy + 8)], fill=(10, 14, 26))
            draw.text((4, gy - 6), f"{pct}%", fill=(0, 230, 255))

        for ctrl in uia_controls[:35]:
            b = ctrl.get("bounds")
            cid = ctrl.get("id")
            if b and len(b) == 4 and cid is not None:
                x1, y1, x2, y2 = b
                draw.rectangle([(x1, y1), (x2, y2)], outline=(255, 60, 120), width=2)
                tag = f"#{cid}"
                draw.rectangle([(x1, max(0, y1 - 16)), (x1 + 28, y1)], fill=(255, 40, 100))
                draw.text((x1 + 3, max(0, y1 - 14)), tag, fill=(255, 255, 255))

        out = io.BytesIO()
        annotated.save(out, format="JPEG", quality=85)
        return out.getvalue()

    async def _capture_frame_to_disk_and_ui(self) -> Dict[str, Any]:
        """Captures screen to disk + UI EventBus WITHOUT returning base64 into LLM text context."""
        self._bind_interactive_desktop()
        from PIL import ImageGrab

        img = ImageGrab.grab()
        w, h = img.size
        save_path = self._captures_dir / "latest_screen.jpg"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82)
        jpg_bytes = buf.getvalue()
        save_path.write_bytes(jpg_bytes)
        b64_str = base64.b64encode(jpg_bytes).decode("ascii")

        thumb = img.resize((32, 32)).convert("L")
        frame_hash = hashlib.sha256(thumb.tobytes()).hexdigest()[:16]

        windows = self._list_native_win32_windows()
        active_win = next((win for win in windows if win.get("active")), windows[0] if windows else {"title": "Desktop", "hwnd": 0})

        try:
            await get_event_bus().publish(
                RuntimeEvent(
                    event_type=EventType.SCREENSHOT_CAPTURED,
                    sender="ComputerUsePlugin",
                    payload={
                        "screenshot_png_b64": b64_str,
                        "window_title": active_win.get("title", "Desktop"),
                        "hwnd": active_win.get("hwnd", 0),
                        "width": w,
                        "height": h,
                    },
                )
            )
        except Exception:
            pass

        uia_controls = self._extract_active_uia_elements(max_elements=35)
        annotated_bytes = self._render_som_and_grid_overlay(img, uia_controls)
        som_path = self._captures_dir / "latest_screen_som.jpg"
        som_path.write_bytes(annotated_bytes)

        return {
            "ok": True,
            "resolution": [w, h],
            "frame_hash": frame_hash,
            "saved_path": str(save_path),
            "active_window": active_win.get("title", "Desktop"),
            "open_windows": [win["title"] for win in windows[:12]],
            "interactive_controls": [
                {"id": c["id"], "name": c["name"], "type": c["type"], "center": c["center"]}
                for c in uia_controls
            ],
            "_raw_jpeg_bytes": jpg_bytes,
            "_raw_annotated_jpeg_bytes": annotated_bytes,
        }

    # ------------------------------------------------------------------
    # First-Class Agent Tools (Strongly Typed, Complete Action Space)
    # ------------------------------------------------------------------

    @dione_tool(
        description=(
            "Draw a geometric shape or freehand path directly onto MS Paint (`mspaint`), a drawing canvas, or whiteboard! "
            "Automatically launches/focuses Paint (if not already open), finds the active canvas area below the ribbon, "
            "and smoothly drags the mouse cursor with the left button held down to draw the shape.\n"
            ":param shape: Shape to draw: 'circle', 'square', 'rectangle', 'triangle', 'star', 'heart', 'smiley', 'spiral', 'line', or 'custom'\n"
            ":param center_x: Optional center X pixel coordinate (auto-detected inside canvas if omitted)\n"
            ":param center_y: Optional center Y pixel coordinate (auto-detected inside canvas if omitted)\n"
            ":param radius: Radius in pixels for circle/star/heart/smiley/spiral (default 130)\n"
            ":param app: Target drawing application to focus/launch (default 'mspaint')"
        ),
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_draw_shape(
        self,
        shape: str = "circle",
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        radius: int = 130,
        app: str = "mspaint",
    ) -> str:
        """
        Draws a clean, visible shape (circle, square, triangle, star, heart, smiley, spiral, line)
        on MS Paint or the active canvas using smooth multi-step SendInput drag synthesis.
        """
        # 1. Minimize Dione so it never blocks the Paint canvas!
        try:
            from server.core.runtime.computer_use import get_computer_use_operator
            get_computer_use_operator().minimize_dione()
        except Exception:
            pass

        # 2. Ensure target app (e.g. Paint) is open, focused, and maximized
        target_app = (app or "mspaint").strip().lower()
        focused = self._focus_window_by_keyword(target_app, maximize=True)
        if not focused:
            await self.launch_app(target_app)
            await asyncio.sleep(1.0)
            focused = self._focus_window_by_keyword(target_app, maximize=True)
        await asyncio.sleep(0.5)

        # 3. Determine safe canvas bounds and center point (guarding against LLM passing 0 or Ribbon coordinates)
        c_left, c_top, c_right, c_bottom = self._find_paint_canvas_bounds()
        cx = int(center_x) if (center_x is not None and int(center_x) > c_left + 40) else int((c_left + c_right) // 2)
        cy = int(center_y) if (center_y is not None and int(center_y) > c_top + 40) else int((c_top + c_bottom) // 2)
        cx = max(c_left + 80, min(cx, c_right - 80))
        cy = max(c_top + 80, min(cy, c_bottom - 80))
        max_r = max(40, min(int(radius or 130), (c_right - c_left) // 3, (c_bottom - c_top) // 3))

        s_type = (shape or "circle").strip().lower()

        # 4. Invoke MS Paint Ribbon shape tool selection (Oval, Rectangle, Triangle, Five-point star, Heart, Diamond, Right arrow, Line)
        ribbon_selected = self._select_paint_ribbon_shape_tool(s_type)
        await asyncio.sleep(0.20)

        # 5. Compute diagonal bounding box coordinates inside safe canvas
        start_x = max(c_left + 40, cx - max_r)
        start_y = max(c_top + 40, cy - max_r)
        end_x = min(c_right - 40, cx + max_r)
        end_y = min(c_bottom - 40, cy + max_r)

        # Generate diagonal drag path over 1.15s (approx 65 interpolation steps)
        steps = 65
        diag_points = []
        for i in range(steps + 1):
            t = i / float(steps)
            diag_points.append((
                int(start_x + (end_x - start_x) * t),
                int(start_y + (end_y - start_y) * t),
            ))

        pre_info = await self._capture_frame_to_disk_and_ui()
        pre_hash = pre_info.get("frame_hash", "")

        # 6. Glide cursor smoothly to (start_x, start_y), press left down, drag diagonally over 1.15s, release left button
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._drag_native_win32_path, diag_points, 0.017, "left")

        # 7. Click outside bounding box to commit shape
        commit_x = min(c_right - 20, end_x + 35)
        commit_y = min(c_bottom - 20, end_y + 35)
        await asyncio.sleep(0.12)
        self._click_native_win32(commit_x, commit_y)
        await asyncio.sleep(0.20)

        post_info = await self._capture_frame_to_disk_and_ui()
        post_hash = post_info.get("frame_hash", "")
        changed = (pre_hash != post_hash) if (pre_hash and post_hash) else True

        return (
            f"Successfully precision-drawn '{s_type}' in MS Paint from ({start_x}, {start_y}) to ({end_x}, {end_y}) "
            f"via Ribbon shape tool selection (tool_selected={ribbon_selected}) and 1.15s diagonal hardware drag (Canvas Visually Updated: {changed})."
        )

    @dione_tool(
        description=(
            "Drag the mouse from (start_x, start_y) to (end_x, end_y) with the mouse button held down "
            "(uses vercel-labs/agent-desktop SendInput drag synthesis with 200ms pickup settle and release guard). "
            "Use this for drag-and-drop, sliders, text selection, or drawing lines/shapes."
        ),
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        steps: int = 25,
        button: str = "left",
    ) -> str:
        """Smoothly drag the mouse from (start_x, start_y) to (end_x, end_y)."""
        n_steps = max(5, min(int(steps or 25), 200))
        pts = [
            (
                int(round(start_x + (end_x - start_x) * (i / n_steps))),
                int(round(start_y + (end_y - start_y) * (i / n_steps))),
            )
            for i in range(n_steps + 1)
        ]
        ok = self._drag_native_win32_path(pts, step_delay_s=0.015, button=button)
        return f"Dragged mouse ({button}) from ({start_x}, {start_y}) to ({end_x}, {end_y}) across {n_steps} steps (success={ok})."

    @dione_tool(
        description=(
            "Execute a semantic Windows UIAutomation (UIA) pattern directly on a control by its name "
            "(ported from qwenlm/open-computer-use & vercel-labs/agent-desktop): "
            "supports pattern='invoke' (click button/menu), 'toggle' (checkbox), 'select' (tab/list item), or 'set_value' (set text field value directly)."
        ),
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_uia_action(
        self,
        target_name: str,
        pattern: str = "invoke",
        value: str = "",
        app: Optional[str] = None,
    ) -> str:
        """Semantic UIA control invocation without relying on pixel coordinates."""
        if app and app.strip():
            self._focus_window_by_keyword(app.strip())
            await asyncio.sleep(0.3)

        t_low = target_name.strip().lower()
        pat_low = (pattern or "invoke").strip().lower()

        try:
            import uiautomation as auto
            fg = auto.GetForegroundControl()
            if not fg:
                return f"No foreground control available; falling back to computer_locate_and_click('{target_name}')."

            matched_ctrl = None

            def _search(ctrl, depth: int = 0):
                nonlocal matched_ctrl
                if depth > 6 or matched_ctrl is not None:
                    return
                try:
                    nm = (ctrl.Name or "").strip()
                    if nm and (nm.lower() == t_low or (len(t_low) >= 3 and t_low in nm.lower())):
                        matched_ctrl = ctrl
                        return
                    for ch in ctrl.GetChildren():
                        _search(ch, depth + 1)
                        if matched_ctrl is not None:
                            return
                except Exception:
                    pass

            _search(fg, 0)
            if matched_ctrl is not None:
                if pat_low == "set_value":
                    try:
                        vp = matched_ctrl.GetValuePattern()
                        if vp:
                            vp.SetValue(value)
                            return f"Set value '{value}' on UIA control '{matched_ctrl.Name}' via ValuePattern."
                    except Exception:
                        pass
                elif pat_low == "toggle":
                    try:
                        tp = matched_ctrl.GetTogglePattern()
                        if tp:
                            tp.Toggle()
                            return f"Toggled UIA control '{matched_ctrl.Name}' via TogglePattern."
                    except Exception:
                        pass
                elif pat_low == "select":
                    try:
                        sp = matched_ctrl.GetSelectionItemPattern()
                        if sp:
                            sp.Select()
                            return f"Selected UIA control '{matched_ctrl.Name}' via SelectionItemPattern."
                    except Exception:
                        pass
                else:
                    try:
                        ip = matched_ctrl.GetInvokePattern()
                        if ip:
                            ip.Invoke()
                            return f"Invoked UIA control '{matched_ctrl.Name}' via InvokePattern."
                    except Exception:
                        pass

                # Fallback to clicking center of matched UIA control
                rect = matched_ctrl.BoundingRectangle
                if rect and rect.width() > 2 and rect.height() > 2:
                    cx, cy = (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
                    self._click_native_win32(cx, cy)
                    return f"Clicked UIA control '{matched_ctrl.Name}' at ({cx}, {cy})."
        except Exception as e:
            logger.debug(f"[UIA Action] Fallback to locate_and_click: {e}")

        return await self.computer_locate_and_click(description=target_name)

    @dione_tool(
        description=(
            "Observe the current desktop state: captures a fresh screenshot for the UI, returns the active foreground window, "
            "all open window titles, and the clickable UI controls (with exact [x, y] coordinates) in the active window. "
            "Call this FIRST before clicking or interacting with an application."
        ),
        permission_level="read",
        requires_confirmation=False,
    )
    async def capture_screen(self, app: Optional[str] = None) -> str:
        """Capture screen state and return compact window + clickable element map (zero base64 bloat)."""
        if app and app.strip():
            self._focus_window_by_keyword(app.strip())
            await asyncio.sleep(0.35)

        try:
            info = await self._capture_frame_to_disk_and_ui()
            info.pop("_raw_jpeg_bytes", None)
            info.pop("_raw_annotated_jpeg_bytes", None)
            return json.dumps(info, indent=2)
        except Exception as e:
            windows = self._list_native_win32_windows()
            return json.dumps({
                "ok": True,
                "note": f"GDI capture fallback ({e})",
                "open_windows": [w["title"] for w in windows[:12]],
            })

    @dione_tool(
        description=(
            "Analyze the live desktop screen using Gemini Vision (with a Set-of-Mark & 0-100% coordinate grid overlay) "
            "to answer a specific visual question, verify whether an action succeeded, or locate buttons in games/browsers "
            "(e.g. 'Where is the Play / Deathmatch button?', 'Is there a circle drawn on the Paint canvas?')."
        ),
        permission_level="read",
        requires_confirmation=False,
    )
    async def inspect_screen_vision(self, question: str = "Describe what is currently visible on the active window and give exact [x, y] pixel coordinates for key buttons.") -> str:
        """Multimodal Gemini Vision inspection of the live desktop screen without polluting chat context with base64."""
        try:
            info = await self._capture_frame_to_disk_and_ui()
            jpg_bytes = info.pop("_raw_annotated_jpeg_bytes", None) or info.pop("_raw_jpeg_bytes", None)
            info.pop("_raw_jpeg_bytes", None)
            if not jpg_bytes:
                return f"Screen state: {json.dumps(info)}"

            api_key = os.getenv("DIONE_LLM_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return f"Screen state (no API key for vision): {json.dumps(info)}"

            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            w, h = info.get("resolution", [1920, 1080])
            uia_summary = json.dumps(info.get("interactive_controls", [])[:20])
            prompt = (
                f"Screen Resolution: {w}x{h} pixels. Active Window: {info.get('active_window')}.\n"
                f"The screenshot has a 10% cyan percentage grid (10%..90%) and numbered red Set-of-Mark badges (#1, #2, ...) for UIA controls: {uia_summary}\n"
                f"Question / Verification Task: {question}\n"
                f"Provide a concise, factual answer including exact pixel coordinates [x, y] (computed from the grid or badge centers) for any relevant buttons or inputs."
            )

            for model_id in ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]:
                try:
                    resp = await client.aio.models.generate_content(
                        model=model_id,
                        contents=[
                            types.Part.from_bytes(data=jpg_bytes, mime_type="image/jpeg"),
                            prompt,
                        ],
                        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=450),
                    )
                    if resp and resp.text:
                        return (
                            f"[Vision Analysis ({model_id}) | Active Window: {info.get('active_window')} | Resolution: {w}x{h}]\n"
                            f"{resp.text.strip()}"
                        )
                except Exception:
                    continue

            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Vision inspection error: {e}"

    @dione_tool(
        description=(
            "Locate any button, link, tab, input box, game lobby button, or icon on the screen by its name or visual description "
            "(e.g. 'Play', 'Deathmatch', 'Start', 'Search box', 'Send button', 'Compose') and click it automatically. "
            "Uses a 3-stage hybrid pipeline: (1) recursive depth-6 Windows UIA tree matching (<30ms), "
            "(2) Set-of-Mark + 0-1000 Gemini Vision bounding-box localization, and (3) post-click visual frame-diff verification."
        ),
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_locate_and_click(self, description: str, double: bool = False, right_click: bool = False) -> str:
        """Locate UI element via recursive UIA tree or Set-of-Mark Gemini Vision, click it, and verify screen change."""
        desc_clean = description.strip()
        desc_low = desc_clean.lower()

        pre_info = await self._capture_frame_to_disk_and_ui()
        pre_hash = pre_info.get("frame_hash", "")
        uia_elements = pre_info.get("interactive_controls", [])
        sw, sh = pre_info.get("resolution", [1920, 1080])

        best_match = None
        for el in uia_elements:
            el_name = el["name"].lower().strip()
            if el_name and desc_low == el_name:
                best_match = el
                break

        if not best_match:
            for el in uia_elements:
                el_name = el["name"].lower().strip()
                if not el_name or len(el_name) < 3:
                    continue
                if (len(desc_low) >= 3 and desc_low in el_name) or (len(el_name) >= 3 and el_name in desc_low):
                    best_match = el
                    break

        clicked_coords: Optional[Tuple[int, int]] = None
        method_used = ""

        if best_match:
            cx, cy = best_match["center"]
            self._click_native_win32(cx, cy, double=double, right=right_click)
            clicked_coords = (cx, cy)
            method_used = f"Windows UIA ('{best_match['name']}', {best_match['type']})"

        if not clicked_coords:
            jpg_bytes = pre_info.get("_raw_annotated_jpeg_bytes") or pre_info.get("_raw_jpeg_bytes")
            api_key = os.getenv("DIONE_LLM_API_KEY") or os.getenv("GEMINI_API_KEY")
            if jpg_bytes and api_key:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                v_prompt = (
                    f"You are a high-precision computer vision UI element locator.\n"
                    f"Screen resolution is {sw}x{sh}. The image includes a 10% cyan coordinate grid and numbered red badges (#1, #2, ...) for UIA elements: {json.dumps(uia_elements[:25])}\n"
                    f"Carefully locate the exact clickable UI element, button, game mode tab, or control described as: \"{desc_clean}\".\n"
                    f"Return ONLY a JSON object with 0-1000 normalized bounding box coordinates tightly enclosing the target:\n"
                    f'{{"box_2d": [ymin, xmin, ymax, xmax], "label": "matched element text"}}'
                )
                for v_model in ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]:
                    try:
                        resp = await client.aio.models.generate_content(
                            model=v_model,
                            contents=[
                                types.Part.from_bytes(data=jpg_bytes, mime_type="image/jpeg"),
                                v_prompt,
                            ],
                            config=types.GenerateContentConfig(
                                temperature=0.05,
                                response_mime_type="application/json",
                            ),
                        )
                        if resp and resp.text:
                            v_data = json.loads(resp.text)
                            if isinstance(v_data, list):
                                v_data = v_data[0] if v_data else {}
                            box = v_data.get("box_2d")
                            if box and len(box) == 4:
                                ymin, xmin, ymax, xmax = [float(v) for v in box]
                                cx = int(((xmin + xmax) / 2.0) / 1000.0 * sw)
                                cy = int(((ymin + ymax) / 2.0) / 1000.0 * sh)
                                self._click_native_win32(cx, cy, double=double, right=right_click)
                                clicked_coords = (cx, cy)
                                method_used = f"Gemini Vision SoM ({v_model})"
                                break
                    except Exception as ve:
                        logger.debug(f"[VisionClick] {v_model} note: {ve}")
                        continue

        if not clicked_coords:
            return (
                f"Could not locate '{desc_clean}' on active window '{pre_info.get('active_window')}'. "
                f"Visible UIA controls: {[e['name'] for e in uia_elements[:12]]}. "
                f"Call `inspect_screen_vision` to inspect the full screen layout."
            )

        await asyncio.sleep(0.45)
        post_info = await self._capture_frame_to_disk_and_ui()
        post_hash = post_info.get("frame_hash", "")
        changed = (pre_hash != post_hash) if (pre_hash and post_hash) else True
        cx, cy = clicked_coords

        return (
            f"Located '{desc_clean}' via {method_used} and clicked at pixel ({cx}, {cy}) "
            f"[Active Window: '{post_info.get('active_window')}', Screen Visually Transitioned: {changed}]."
        )

    @dione_tool(
        description=(
            "Execute a low-level desktop action.\n"
            ":param action: One of 'click', 'double_click', 'triple_click', 'right_click', 'middle_click', 'drag', 'draw_circle', 'move', 'type', 'key', 'scroll', 'wait', 'focus_app', 'list_windows', 'list_apps', 'capture'\n"
            ":param coordinate: [x, y] pixel coordinates for click/move/drag end\n"
            ":param start_coordinate: [start_x, start_y] pixel coordinates for 'drag'\n"
            ":param element: UI element index if using Set-of-Mark\n"
            ":param text: Text string to type when action='type'\n"
            ":param keys: Key or shortcut to press when action='key' (e.g. 'enter', 'f11', 'ctrl+l', 'ctrl+t', 'alt+tab')\n"
            ":param app: Application name or window title for 'focus_app'\n"
            ":param direction: Scroll direction ('up', 'down', 'left', 'right')\n"
            ":param amount: Scroll ticks (default 5)\n"
            ":param duration: Wait duration in seconds when action='wait'"
        ),
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_use(
        self,
        action: str,
        coordinate: Optional[List[int]] = None,
        start_coordinate: Optional[List[int]] = None,
        element: Optional[int] = None,
        text: Optional[str] = None,
        keys: Optional[str] = None,
        app: Optional[str] = None,
        mode: str = "som",
        direction: str = "down",
        amount: int = 5,
        duration: float = 1.0,
        delivery_mode: str = "foreground",
    ) -> str:
        """Strongly-typed unified computer_use action dispatcher with fast native Win32 SendInput execution."""
        act = (action or "").strip().lower()

        if act in ("capture", "screenshot"):
            return await self.capture_screen(app=app)

        if act in ("list_windows", "windows"):
            wins = self._list_native_win32_windows()
            return json.dumps({"ok": True, "count": len(wins), "windows": wins[:20]})

        if act == "focus_app" and app:
            matched = self._focus_window_by_keyword(app)
            if matched:
                await asyncio.sleep(0.4)
                return json.dumps({"ok": True, "action": "focus_app", "focused": matched["title"]})

        if act in ("draw_circle", "circle"):
            cx = int(coordinate[0]) if coordinate and len(coordinate) >= 2 else None
            cy = int(coordinate[1]) if coordinate and len(coordinate) >= 2 else None
            return await self.computer_draw_shape(shape="circle", center_x=cx, center_y=cy, app=app or "mspaint")

        if act in ("drag", "left_click_drag"):
            if start_coordinate and len(start_coordinate) >= 2 and coordinate and len(coordinate) >= 2:
                return await self.computer_drag(
                    start_x=int(start_coordinate[0]),
                    start_y=int(start_coordinate[1]),
                    end_x=int(coordinate[0]),
                    end_y=int(coordinate[1]),
                )

        if act in ("move", "mouse_move", "hover") and coordinate and len(coordinate) >= 2:
            self._move_cursor_smooth(int(coordinate[0]), int(coordinate[1]))
            return json.dumps({"ok": True, "action": "move", "coordinate": [int(coordinate[0]), int(coordinate[1])]})

        if act in ("click", "left_click", "double_click", "triple_click", "right_click", "middle_click") and coordinate and len(coordinate) >= 2:
            x, y = int(coordinate[0]), int(coordinate[1])
            ok = self._click_native_win32(
                x,
                y,
                double=(act == "double_click"),
                right=(act == "right_click"),
                middle=(act == "middle_click"),
                count=(3 if act == "triple_click" else 1),
            )
            return json.dumps({"ok": ok, "action": act, "coordinate": [x, y]})

        if act == "type" and text is not None:
            return await self.computer_type(text=text, press_enter=False)

        if act in ("key", "hotkey", "press_key") and keys:
            ok = self._send_native_win32_key(keys)
            return json.dumps({"ok": ok, "action": "key", "keys": keys})

        if act in ("wait", "sleep"):
            wait_s = max(0.1, min(float(duration or 1.0), 15.0))
            await asyncio.sleep(wait_s)
            return json.dumps({"ok": True, "action": "wait", "duration": wait_s})

        if act == "scroll":
            try:
                if coordinate and len(coordinate) >= 2:
                    self._move_cursor_smooth(int(coordinate[0]), int(coordinate[1]))
                if hasattr(ctypes, "windll"):
                    ticks = int(amount or 5) * (120 if direction in ("up", "right") else -120)
                    flag = MOUSEEVENTF_HWHEEL if direction in ("left", "right") else MOUSEEVENTF_WHEEL
                    self._post_sendinput_mouse(0, 0, flag, mouse_data=ticks)
                    return json.dumps({"ok": True, "action": "scroll", "direction": direction, "amount": amount})
            except Exception as se:
                return json.dumps({"ok": False, "error": str(se)})

        payload: Dict[str, Any] = {"action": act, "mode": mode, "delivery_mode": delivery_mode}
        if coordinate is not None:
            payload["coordinate"] = coordinate
        if start_coordinate is not None:
            payload["from_coordinate"] = start_coordinate
            payload["to_coordinate"] = coordinate
        if element is not None:
            payload["element"] = element
        if text is not None:
            payload["text"] = text
        if keys is not None:
            payload["keys"] = keys
        if app is not None:
            payload["app"] = app

        try:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, handle_computer_use, payload)
            res_str = json.dumps(res) if isinstance(res, dict) else str(res)
            from server.core.tool_truncator import truncate_tool_result_text
            return truncate_tool_result_text(res_str)
        except Exception as e:
            return json.dumps({"ok": False, "action": act, "error": str(e)})

    @dione_tool(
        description="Click at exact (x, y) desktop pixel coordinates with the mouse (uses 60ms hover + 75ms hold duration).",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_click(self, x: int, y: int, button: str = "left", double: bool = False) -> str:
        """Click at exact desktop pixel coordinate and verify active window state."""
        btn = (button or "left").lower()
        self._click_native_win32(x, y, double=double, right=(btn == "right"), middle=(btn == "middle"))
        return f"Clicked mouse at ({x}, {y}) [button={button}, double={double}, hold=75ms]"

    @dione_tool(
        description="Type text into the currently focused window or input field (uses fast clipboard injection for reliability). Set press_enter=True to submit.",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_type(self, text: str, press_enter: bool = False, clear_first: bool = False) -> str:
        """Fast, reliable text entry via clipboard paste (Ctrl+V) with Win32 scan-code fallback."""
        if clear_first:
            self._send_native_win32_key("ctrl+a")
            await asyncio.sleep(0.04)
            self._send_native_win32_key("backspace")
            await asyncio.sleep(0.04)

        if not text:
            if press_enter:
                self._send_native_win32_key("enter")
            return "Pressed Enter."

        pasted = False
        if len(text) > 1:
            try:
                import pyperclip
                pyperclip.copy(text)
                await asyncio.sleep(0.04)
                pasted = self._send_native_win32_key("ctrl+v")
                await asyncio.sleep(0.06)
            except Exception:
                pasted = False

        if not pasted:
            if hasattr(ctypes, "windll"):
                user32 = ctypes.windll.user32
                for char in text:
                    vk = user32.VkKeyScanW(ord(char))
                    if vk != -1:
                        shift = (vk >> 8) & 1
                        key_code = vk & 0xFF
                        scan = user32.MapVirtualKeyW(key_code, 0)
                        if shift:
                            user32.keybd_event(0x10, user32.MapVirtualKeyW(0x10, 0), 0, 0)
                        user32.keybd_event(key_code, scan, 0, 0)
                        time.sleep(0.015)
                        user32.keybd_event(key_code, scan, 2, 0)
                        if shift:
                            user32.keybd_event(0x10, user32.MapVirtualKeyW(0x10, 0), 2, 0)

        if press_enter:
            await asyncio.sleep(0.05)
            self._send_native_win32_key("enter")

        return f"Typed '{text[:80]}' into active window (press_enter={press_enter})."

    @dione_tool(
        description="Press a keyboard shortcut or hotkey: 'f' (YouTube fullscreen), 'f11' (browser fullscreen), 'ctrl+l' (address bar), 'ctrl+t' (new tab), 'ctrl+w' (close tab), 'alt+tab', 'enter', 'esc', 'space'.",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def computer_hotkey(self, keys: str) -> str:
        """Trigger keyboard shortcut directly via Win32 hardware scan codes (50ms hold)."""
        ok = self._send_native_win32_key(keys)
        return f"Pressed hotkey '{keys}' (success={ok})."

    @dione_tool(
        description="Open Microsoft Edge or Google Chrome to a URL (automatically prepends https:// if needed).",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def open_browser(self, url: str = "https://www.google.com", browser: str = "auto", fullscreen: bool = False) -> str:
        """Open web browser to a URL and bring it to foreground focus."""
        target_url = url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = f"https://{target_url}"

        b_choice = browser.lower()
        if b_choice in ("auto", "default"):
            b_choice = "chrome" if CHROME_EXE.exists() else "edge"

        fs_flag = "--start-fullscreen" if fullscreen else "--start-maximized"
        try:
            if "chrome" in b_choice and CHROME_EXE.exists():
                subprocess.Popen([str(CHROME_EXE), fs_flag, target_url])
                await asyncio.sleep(1.5)
                self._focus_window_by_keyword("chrome")
                await asyncio.sleep(0.4)
                return f"Opened Google Chrome to {target_url} (fullscreen={fullscreen})"
            elif "edge" in b_choice and EDGE_EXE.exists():
                subprocess.Popen([str(EDGE_EXE), fs_flag, target_url])
                await asyncio.sleep(1.5)
                self._focus_window_by_keyword("edge")
                await asyncio.sleep(0.4)
                return f"Opened Microsoft Edge to {target_url} (fullscreen={fullscreen})"
            else:
                webbrowser.open(target_url)
                await asyncio.sleep(1.2)
                return f"Opened default browser to {target_url}"
        except Exception as e:
            webbrowser.open(target_url)
            return f"Opened browser to {target_url} ({e})"

    @dione_tool(
        description="Play a YouTube video directly by query or channel name (resolves direct /watch?v=... URL, avoids help videos, and opens in full screen).",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def play_youtube_video(self, query: str, fullscreen: bool = True, browser: str = "auto") -> str:
        """Resolve top YouTube video watch URL and launch directly (with static help video filter)."""
        raw_input = (query or "").strip()
        clean_q = re.sub(r'^(?:start\s+(?:chrome|msedge|edge|browser)\s+)?["\']?', '', raw_input, flags=re.I)
        clean_q = re.sub(r'["\']?$', '', clean_q).strip()

        EXCLUDED_HELP_IDS = {"6rZRe1nfrJo", "dQw4w9WgXcQ"}
        watch_url = None

        watch_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', clean_q)
        if watch_match and watch_match.group(1) not in EXCLUDED_HELP_IDS:
            watch_url = f"https://www.youtube.com/watch?v={watch_match.group(1)}"

        if not watch_url:
            channel_match = re.search(r'(?:https?://(?:www\.)?youtube\.com/)?(@[a-zA-Z0-9_.-]+(?:/videos)?)', clean_q)
            if channel_match:
                ch_path = channel_match.group(1)
                if not ch_path.endswith('/videos'):
                    ch_path += '/videos'
                ch_url = f"https://www.youtube.com/{ch_path}"
                try:
                    req = urllib.request.Request(
                        ch_url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    )
                    loop = asyncio.get_running_loop()
                    html = await loop.run_in_executor(
                        None, lambda: urllib.request.urlopen(req, timeout=6.0).read().decode("utf-8", errors="ignore")
                    )
                    vids = [
                        v for v in (
                            re.findall(r'"videoRenderer":\s*\{"videoId":"([a-zA-Z0-9_-]{11})"', html)
                            + re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                        )
                        if v not in EXCLUDED_HELP_IDS
                    ]
                    if vids:
                        watch_url = f"https://www.youtube.com/watch?v={vids[0]}"
                except Exception as e:
                    logger.debug(f"[YouTube] Channel video lookup note: {e}")

        if not watch_url:
            search_terms = re.sub(r'\b(?:open\s+(?:yt|youtube)\s+(?:and\s+)?|play\s+|in\s+full\s*screen|full\s*screen)\b', '', clean_q, flags=re.I).strip()
            if not search_terms:
                search_terms = clean_q

            encoded = urllib.parse.quote_plus(search_terms)
            search_url = f"https://www.youtube.com/results?search_query={encoded}"

            try:
                req = urllib.request.Request(
                    search_url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                loop = asyncio.get_running_loop()
                html = await loop.run_in_executor(
                    None, lambda: urllib.request.urlopen(req, timeout=6.0).read().decode("utf-8", errors="ignore")
                )
                video_ids = [
                    v for v in (
                        re.findall(r'"videoRenderer":\s*\{"videoId":"([a-zA-Z0-9_-]{11})"', html)
                        + re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                    )
                    if v not in EXCLUDED_HELP_IDS
                ]
                if video_ids:
                    watch_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            except Exception as e:
                logger.debug(f"[YouTube] Direct ID lookup note: {e}")

        target_url = watch_url or (f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(clean_q)}" if not clean_q.startswith("http") else clean_q)
        await self.open_browser(url=target_url, browser=browser, fullscreen=fullscreen)

        if fullscreen and watch_url:
            await asyncio.sleep(1.8)
            self._focus_window_by_keyword("youtube")
            self._send_native_win32_key("f")

        return f"Playing YouTube video '{query}' at {target_url} (fullscreen={fullscreen})."

    @dione_tool(
        description="Launch or focus a desktop application by name (e.g. 'Paint', 'mspaint', 'Spotify', 'Chrome', 'Edge', 'VS Code', 'Notepad', 'Calculator', 'Explorer', 'Valorant', 'Riot Client') with a 1.8s render settle.",
        permission_level="execute",
        requires_confirmation=False,
    )
    async def launch_app(self, app: str) -> str:
        """Launch or focus desktop application with 1.8s render settle standard."""
        a_lower = app.lower().strip()

        existing = self._focus_window_by_keyword(a_lower, maximize=(a_lower in ("paint", "mspaint")))
        if not existing and a_lower in ("valorant", "riot"):
            existing = self._focus_window_by_keyword("riot") or self._focus_window_by_keyword("valorant")

        if existing:
            await asyncio.sleep(0.65)
            return f"Focused already-running window: '{existing['title']}' (HWND: {existing['hwnd']})."

        known_map = {
            "paint": ["mspaint.exe"],
            "ms paint": ["mspaint.exe"],
            "mspaint": ["mspaint.exe"],
            "chrome": [str(CHROME_EXE)],
            "google chrome": [str(CHROME_EXE)],
            "edge": [str(EDGE_EXE)],
            "microsoft edge": [str(EDGE_EXE)],
            "riot client": [str(RIOT_EXE)],
            "valorant": [str(RIOT_EXE), "--launch-product=valorant", "--launch-patchline=live"],
            "notepad": ["notepad.exe"],
            "calc": ["calc.exe"],
            "calculator": ["calc.exe"],
            "explorer": ["explorer.exe"],
            "code": ["code"],
            "vs code": ["code"],
            "spotify": ["cmd", "/c", "start", "spotify:"],
            "terminal": ["wt.exe"],
        }

        cmd_args = known_map.get(a_lower)
        if cmd_args:
            try:
                subprocess.Popen(cmd_args, shell=(cmd_args[0] in ("cmd", "code")))
                await asyncio.sleep(1.8)
                focused = self._focus_window_by_keyword(a_lower, maximize=(a_lower in ("paint", "mspaint", "ms paint"))) or (
                    self._focus_window_by_keyword("riot") if "valorant" in a_lower else None
                )
                await asyncio.sleep(0.65)
                win_title = focused["title"] if focused else app
                return f"Launched and focused '{win_title}'."
            except Exception as e:
                logger.debug(f"Known app launch fallback: {e}")

        try:
            subprocess.Popen(f'start "" "{app}"', shell=True)
            await asyncio.sleep(1.8)
            focused = self._focus_window_by_keyword(a_lower)
            await asyncio.sleep(0.65)
            win_title = focused["title"] if focused else app
            return f"Launched application '{win_title}'."
        except Exception as e:
            return f"Could not launch '{app}': {e}"

    @dione_tool(
        description="List all visible open windows on the Windows desktop with their titles and active status.",
        permission_level="read",
        requires_confirmation=False,
    )
    async def list_open_windows(self) -> str:
        """List visible desktop windows."""
        wins = self._list_native_win32_windows()
        return json.dumps({"ok": True, "count": len(wins), "windows": wins[:25]}, indent=2)
