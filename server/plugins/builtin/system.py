"""
Dione AI — System Plugin (Sovereign v5.0 Open-CUA Edition)

Provides hardened system-level operations:
- Real-time hardware telemetry (CPU, RAM, GPU, Battery, Disk, Network, Uptime)
- Poset Lattice gated command execution with sub-process tree safety
- Smart Auto-Routing for MS Paint drawing, mouse dragging, app launching, and keystrokes
  so the agent NEVER gets stuck in a Guardrail 2 refusal loop if it calls `run_command`!
"""

import os
import sys
import re
import urllib.parse
import time
import shutil
import platform
import asyncio
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
import psutil

from server.plugins.base import BasePlugin, dione_tool
from server.core.safety import SafetyKernel, PermissionTier


class SystemPlugin(BasePlugin):
    """System-level operations, hardware perception, and process control."""

    name = "SystemPlugin"
    description = "Execute verified system commands, monitor hardware telemetry, and manage processes"
    version = "5.0.0"

    def __init__(self):
        super().__init__()
        self._safety = SafetyKernel()

    def _get_gpu_telemetry(self) -> str:
        """Query genuine GPU telemetry via nvidia-smi or Windows CimInstance."""
        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi:
            try:
                cmd = [
                    nvidia_smi,
                    "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
                    gpu_reports = []
                    for line in lines:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 5:
                            gpu_reports.append(
                                f"{parts[0]} | Temp: {parts[1]} C | Load: {parts[2]}% | VRAM: {parts[3]}MB / {parts[4]}MB"
                            )
                        else:
                            gpu_reports.append(line)
                    return "; ".join(gpu_reports)
            except Exception as e:
                logger.debug(f"[SystemPlugin] nvidia-smi query skipped: {e}")

        if platform.system() == "Windows":
            try:
                ps_cmd = (
                    "Get-CimInstance Win32_VideoController | "
                    "Select-Object -Property Name, AdapterRAM | "
                    "ForEach-Object { $_.Name + ' (' + [math]::Round($_.AdapterRAM/1GB, 1) + ' GB)' }"
                )
                res = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=4,
                )
                if res.returncode == 0 and res.stdout.strip():
                    lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
                    return " | ".join(lines)
            except Exception as e:
                logger.debug(f"[SystemPlugin] CimInstance GPU query skipped: {e}")

        return "GPU telemetry unavailable / Standard Display Device"

    def _get_battery_telemetry(self) -> str:
        """Retrieve genuine battery and power adapter status."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "AC Powered (Desktop / No Battery Detected)"
            status = "Plugged in (Charging/Full)" if battery.power_plugged else "On Battery"
            if battery.secsleft > 0 and not battery.power_plugged:
                hrs = battery.secsleft // 3600
                mins = (battery.secsleft % 3600) // 60
                time_str = f" (~{hrs}h {mins}m remaining)"
            else:
                time_str = ""
            return f"{battery.percent}% [{status}]{time_str}"
        except Exception as e:
            return f"Battery status unavailable ({e})"

    def _get_uptime(self) -> str:
        """Calculate system uptime from boot time."""
        try:
            boot_timestamp = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_timestamp)
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            parts.append(f"{minutes}m")
            return " ".join(parts) or "< 1m"
        except Exception:
            return "Uptime unavailable"

    @dione_tool(
        description="Get comprehensive real-time system and hardware telemetry (CPU, RAM, GPU, Battery, Disk, Network)",
        permission_level="read",
    )
    async def system_info(self) -> str:
        """Get genuine real-time hardware status and operating system specifications."""
        try:
            root_drive = os.environ.get("SystemDrive", "C:") + ("\\" if platform.system() == "Windows" else "/")
            disk = psutil.disk_usage(root_drive)
            vmem = psutil.virtual_memory()
            net_io = psutil.net_io_counters()
            sent_mb = round(net_io.bytes_sent / (1024 * 1024), 1)
            recv_mb = round(net_io.bytes_recv / (1024 * 1024), 1)

            info = {
                "OS": f"{platform.system()} {platform.release()} (Build {platform.version()})",
                "Hostname": platform.node(),
                "Architecture": platform.machine(),
                "Uptime": self._get_uptime(),
                "CPU": f"{psutil.cpu_count(logical=False)} cores ({psutil.cpu_count(logical=True)} threads) @ {psutil.cpu_percent(interval=0.1)}% utilization",
                "RAM": f"{round((vmem.total - vmem.available) / (1024**3), 1)} GB / {round(vmem.total / (1024**3), 1)} GB ({vmem.percent}% used)",
                "System Disk": f"{round(disk.used / (1024**3), 1)} GB / {round(disk.total / (1024**3), 1)} GB ({disk.percent}% used, Drive {root_drive})",
                "Battery": self._get_battery_telemetry(),
                "GPU": self._get_gpu_telemetry(),
                "Network Traffic": f"Sent: {sent_mb} MB | Received: {recv_mb} MB",
                "Python Runtime": platform.python_version(),
            }

            lines = [f"  * {k}: {v}" for k, v in info.items()]
            return "=== Hardware & System Telemetry ===\n" + "\n".join(lines)
        except Exception as e:
            logger.error(f"[SystemPlugin] Failed to read system telemetry: {e}")
            return f"Error retrieving system telemetry: {e}"

    @dione_tool(
        description=(
            "Run a non-interactive terminal/CLI command for developer operations (git, npm, pip, project builds, directory analysis). "
            "NOTE: For desktop GUI actions, prefer ComputerUsePlugin tools (`computer_draw_shape`, `computer_drag`, `computer_locate_and_click`, "
            "`computer_click`, `computer_hotkey`, `launch_app`, `play_youtube_video`)."
        ),
        requires_confirmation=False,
        permission_level="execute",
    )
    async def run_command(self, command: str, timeout: int = 30) -> str:
        """Execute a verified shell command or auto-route GUI automation commands to ComputerUsePlugin."""
        cmd_lower = command.lower().strip()

        from server.plugins.builtin.computer_use_plugin import ComputerUsePlugin
        cup = ComputerUsePlugin()

        # Auto-Router 0: Intercept Paint / Shape / Circle drawing scripts or commands in run_command!
        all_shapes = ("circle", "square", "rectangle", "triangle", "star", "heart", "smiley", "spiral", "house", "diamond", "arrow", "line")
        for shape_kw in all_shapes:
            if shape_kw in cmd_lower and any(k in cmd_lower for k in ("mspaint", "paint", "pyautogui", "ctypes", "mouse_event", "cos", "sin", "drag", "draw")):
                res = await cup.computer_draw_shape(shape=shape_kw, app="mspaint")
                return f"[Auto-Routed to ComputerUsePlugin.computer_draw_shape] {res}"

        if ("math.cos" in cmd_lower or "math.sin" in cmd_lower) and any(k in cmd_lower for k in ("pyautogui", "ctypes", "mouse_event", "setcursorpos")):
            res = await cup.computer_draw_shape(shape="circle", app="mspaint")
            return f"[Auto-Routed to ComputerUsePlugin.computer_draw_shape] {res}"

        # Auto-Router 0.5: Intercept GUI app launches (start mspaint, mspaint, notepad, calc, etc.) to prevent subprocess hanging
        gui_launch_match = re.search(r"^(?:start(?:-process)?\s+)?['\"]?(mspaint|paint|notepad|calc|calculator|explorer|chrome|msedge|code)(?:\.exe)?['\"]?$", cmd_lower)
        if gui_launch_match and not any(k in cmd_lower for k in ("http://", "https://", "youtube")):
            app_target = gui_launch_match.group(1)
            res = await cup.launch_app(app=app_target)
            return f"[Auto-Routed to ComputerUsePlugin.launch_app] {res}"

        # Auto-Router 1: Intercept browser / video launches via raw command and execute cleanly
        if any(b in cmd_lower for b in ["start chrome", "start msedge", "start edge", "youtube.com", "http://", "https://"]):
            if "youtube" in cmd_lower or "watch" in cmd_lower or "video" in cmd_lower:
                url_match = re.search(r'https?://[^\s"\'<>]+', command)
                if url_match and ("youtube.com" in url_match.group(0).lower() or "youtu.be" in url_match.group(0).lower()):
                    res = await cup.play_youtube_video(query=url_match.group(0), fullscreen=True)
                    return f"[Auto-Routed to ComputerUsePlugin] {res}"

                yt_search = re.search(r'search_query=([^"\'&\s]+)', command)
                yt_watch = re.search(r'v=([a-zA-Z0-9_-]{11})', command)
                if yt_search:
                    raw_q = urllib.parse.unquote_plus(yt_search.group(1))
                    res = await cup.play_youtube_video(query=raw_q, fullscreen=True)
                    return f"[Auto-Routed to ComputerUsePlugin] {res}"
                elif yt_watch:
                    vid_url = f"https://www.youtube.com/watch?v={yt_watch.group(1)}"
                    res = await cup.open_browser(url=vid_url)
                    return f"[Auto-Routed to ComputerUsePlugin] Successfully launched video {vid_url} in browser."
                else:
                    clean_query = re.sub(r'^(?:start\s+(?:chrome|msedge|edge|browser)\s+)?["\']?', '', command.strip(), flags=re.I)
                    clean_query = re.sub(r'["\']?$', '', clean_query).strip()
                    res = await cup.play_youtube_video(query=clean_query, fullscreen=True)
                    return f"[Auto-Routed to ComputerUsePlugin] {res}"
            url_match = re.search(r'https?://[^\s"\'<>]+', command)
            if url_match:
                target_url = url_match.group(0)
                res = await cup.open_browser(url=target_url)
                return f"[Auto-Routed to ComputerUsePlugin] {res}"

        # Auto-Router 2: Intercept raw GUI automation scripts (pyautogui, ctypes, SendKeys, SetCursorPos, etc.)
        gui_keywords = [
            "pyautogui", "ctypes", "sendkeys", "sendwait", "win32gui", "win32con",
            "keybd_event", "mouse_event", "setcursorpos", "pynput", "enumwindows",
            "getwindowswithtitle", "add-type", "user32.dll", "user32", "wscript.shell"
        ]
        if any(k in cmd_lower for k in gui_keywords):
            logger.info(f"[SystemPlugin] Auto-routing GUI script in run_command: {command[:120]}")

            # 2.0 AppActivate / SetForegroundWindow
            fw_match = re.search(r'(?:AppActivate|SetForegroundWindow|FindWindow)\s*\(?\s*[\'"]([^\'"]+)[\'"]\s*\)?', command, re.I)
            if fw_match:
                app_name = fw_match.group(1)
                res = await cup.launch_app(app=app_name)
                return f"[Auto-Routed to ComputerUsePlugin.launch_app] Focused application '{app_name}' directly: {res}"

            # 2.1 Mouse drag in PyAutoGUI (dragTo / dragRel)
            drag_to_m = re.search(r'moveTo\s*\(\s*(\d+)\s*,\s*(\d+).*?dragTo\s*\(\s*(\d+)\s*,\s*(\d+)', command, re.I | re.S)
            if drag_to_m:
                sx, sy, ex, ey = [int(v) for v in drag_to_m.groups()]
                res = await cup.computer_drag(start_x=sx, start_y=sy, end_x=ex, end_y=ey)
                return f"[Auto-Routed to ComputerUsePlugin.computer_drag] {res}"

            # 2.2 Key presses in SendKeys, PyAutoGUI, etc.
            key_match = re.search(r'(?:SendWait|SendKeys|Send|press|hotkey)\s*\(?[\'"]\{?([a-zA-Z0-9_+^%~ -]+)\}?[\'"]\)?', command, re.I)
            if key_match:
                extracted_key = key_match.group(1).lower().strip()
                key_map = {
                    "enter": "enter", "return": "enter", "esc": "escape", "escape": "escape",
                    "tab": "tab", "space": "space", "f11": "f11", "f5": "f5", "backspace": "backspace",
                    "up": "up", "down": "down", "left": "left", "right": "right",
                }
                mapped_key = key_map.get(extracted_key, extracted_key)
                if len(mapped_key) <= 10 and not any(c in mapped_key for c in (" ", "\t", "\n")):
                    res = await cup.computer_use(action="key", keys=mapped_key)
                    return f"[Auto-Routed to ComputerUsePlugin.computer_use] Executed key '{mapped_key}' directly: {res}"
                else:
                    res = await cup.computer_type(text=key_match.group(1))
                    return f"[Auto-Routed to ComputerUsePlugin.computer_type] Typed text directly: {res}"

            # 2.3 Mouse clicks / coordinates in PyAutoGUI / SetCursorPos / mouse_event
            cursor_match = re.search(r'SetCursorPos\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', command, re.I)
            if cursor_match and "for " not in cmd_lower and "while " not in cmd_lower:
                cx, cy = int(cursor_match.group(1)), int(cursor_match.group(2))
                res = await cup.computer_click(x=cx, y=cy)
                return f"[Auto-Routed to ComputerUsePlugin.computer_click] Clicked at ({cx}, {cy}) directly: {res}"

            click_match = re.search(r'click\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', command, re.I)
            if click_match:
                cx, cy = int(click_match.group(1)), int(click_match.group(2))
                res = await cup.computer_click(x=cx, y=cy)
                return f"[Auto-Routed to ComputerUsePlugin.computer_click] Clicked at ({cx}, {cy}) directly: {res}"

            # 2.4 If the script is a loop/canvas drawing script (contains `for ` or `range(` and mouse moves/clicks), route to computer_draw_shape!
            if ("for " in cmd_lower or "range(" in cmd_lower) and any(k in cmd_lower for k in ("mouse", "cursor", "drag", "move")):
                res = await cup.computer_draw_shape(shape="circle", app="mspaint")
                return f"[Auto-Routed to ComputerUsePlugin.computer_draw_shape] {res}"

            # 2.5 Typing in PyAutoGUI
            type_match = re.search(r'(?:typewrite|write)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', command, re.I)
            if type_match:
                txt = type_match.group(1)
                res = await cup.computer_type(text=txt)
                return f"[Auto-Routed to ComputerUsePlugin.computer_type] Typed text directly: {res}"

            if any(k in cmd_lower for k in ["f11", "0x7a", "fullscreen"]):
                res = await cup.computer_use(action="key", keys="f11")
                return f"[Auto-Routed to ComputerUsePlugin.computer_use] Triggered F11 full-screen shortcut directly: {res}"

            if any(k in cmd_lower for k in ["screenshot", "desktop_view", "imagegrab"]):
                res = await cup.capture_screen()
                return f"[Auto-Routed to ComputerUsePlugin.capture_screen] Captured desktop view: {res[:200]}..."

        # 1. Prompt Injection Defense
        if self._safety.detect_prompt_injection(command):
            logger.warning(f"[SystemPlugin] Blocked potential injection command: {command}")
            return f"SECURITY ALERT: Shell command '{command}' contains disallowed injection syntax."

        # 2. Poset Lattice Validation
        check = self._safety.validate_command(command)
        if not check.allowed:
            logger.warning(f"[SystemPlugin] Safety Lattice rejected command `{command}`: {check.action_summary}")
            return f"SAFETY REJECTED: Command execution denied ({check.action_summary})."

        logger.info(f"[SystemPlugin] Executing command: {command} (Tier: {check.required_tier.name})")

        start_time = time.time()
        try:
            loop = asyncio.get_running_loop()

            def _sync_exec():
                return subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    errors="replace",
                )

            res = await loop.run_in_executor(None, _sync_exec)
            duration = round(time.time() - start_time, 2)
            out_str = (res.stdout or "").strip()
            err_str = (res.stderr or "").strip()

            result = f"Command: {command}\nExit code: {res.returncode} (took {duration}s)\n"
            if out_str:
                result += f"Output:\n{out_str}\n"
            if err_str:
                result += f"Errors:\n{err_str}\n"

            return result.strip()

        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds and was forcefully terminated."
        except Exception as e:
            logger.error(f"[SystemPlugin] Subprocess execution error: {repr(e)}")
            return f"Command failed to execute: {e or repr(e)}"

    @dione_tool(
        description="Get current precise date, time, timezone, and calendar perception",
        permission_level="read",
    )
    async def get_datetime(self) -> str:
        """Get the current date, time, day of the week, and local timezone offset."""
        now = datetime.now()
        tz_name = now.astimezone().tzname() or "Local"
        tz_offset = now.astimezone().strftime("%z")
        return (
            f"Current DateTime: {now.strftime('%A, %B %d, %Y at %I:%M:%S %p')} "
            f"({tz_name}, UTC{tz_offset})"
        )

    @dione_tool(
        description="List active system processes sorted by CPU or Memory consumption",
        permission_level="read",
    )
    async def list_processes(self, top_n: int = 10, sort_by: str = "memory", limit: Optional[int] = None) -> str:
        """List top processes by CPU or memory usage."""
        if limit is not None:
            top_n = limit
        metric = "cpu_percent" if sort_by.lower() == "cpu" else "memory_percent"
        processes: List[Dict[str, Any]] = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                info = proc.info
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x.get(metric, 0) or 0, reverse=True)
        top = processes[: max(1, min(top_n, 50))]

        header = f"Top {len(top)} processes sorted by {sort_by.upper()}:"
        lines = [header]
        for p in top:
            pid = p.get("pid", 0)
            name = p.get("name", "unknown")
            cpu = p.get("cpu_percent", 0.0) or 0.0
            ram = p.get("memory_percent", 0.0) or 0.0
            status = p.get("status", "running")
            lines.append(f"  PID {pid:6d} | {name:<25} | CPU: {cpu:5.1f}% | RAM: {ram:5.1f}% | {status}")

        return "\n".join(lines)

    @dione_tool(
        description="Gracefully terminate or kill a running system process by PID",
        requires_confirmation=True,
        permission_level="privileged",
    )
    async def kill_process(self, pid: int, force: bool = False) -> str:
        """Terminate a process by PID after safety verification."""
        current_pid = os.getpid()
        if pid in (0, 4, current_pid):
            return f"SAFETY REFUSAL: Cannot terminate critical process PID {pid} (Protected Core PID)."

        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
        except psutil.NoSuchProcess:
            return f"Process with PID {pid} does not exist."
        except psutil.AccessDenied:
            return f"ACCESS DENIED: Insufficient permissions to inspect PID {pid}."

        logger.warning(f"[SystemPlugin] Attempting to terminate PID {pid} ({proc_name}), force={force}")

        try:
            if force:
                proc.kill()
                return f"Process {proc_name} (PID {pid}) was forcefully killed (SIGKILL)."
            proc.terminate()
            gone, alive = psutil.wait_procs([proc], timeout=3)
            if proc in gone:
                return f"Process {proc_name} (PID {pid}) terminated successfully."
            proc.kill()
            return f"Process {proc_name} (PID {pid}) did not respond to SIGTERM; forcefully killed."
        except psutil.NoSuchProcess:
            return f"Process {proc_name} (PID {pid}) has already exited."
        except psutil.AccessDenied:
            return f"ACCESS DENIED: Administrator rights required to terminate {proc_name} (PID {pid})."
        except Exception as e:
            return f"Failed to terminate PID {pid}: {e}"

    get_system_info = system_info
    system_get_datetime = get_datetime
