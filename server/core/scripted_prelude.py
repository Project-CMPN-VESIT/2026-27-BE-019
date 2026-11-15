"""
Dione AI — Hermes Scripted Prelude & Deterministic Live-Demo Fast-Path (`turn_scripted_prelude.py`)
===================================================================================================
Ported from NousResearch/hermes-agent (`agent/turn_scripted_prelude.py`).

Why this exists:
During a live presentation or professor review, when the user issues a clear desktop, media,
or workspace command (including multi-step compound prompts like "open paint and draw a circle and a star",
"open notepad and write hello professor", "play interstellar on youtube", "check my system info",
"search my google drive", "show my recent google photos", or "use execute_code to..."),
waiting on multiple LLM round-trips risks:
  1. Model hesitation or redundant tool calls,
  2. API rate-limit (429) delays, or
  3. Empty post-tool text responses that leave the UI on "Thinking...".

`run_demo_scripted_prelude` runs BEFORE the first model call:
- Parses single or multi-clause commands into a deterministic sequence of `(tool_name, args)` calls.
- Invokes the engine's wrapped tool callables directly so every `EngineStep` (`ACTING` -> `OBSERVING`),
  live screenshot capture, and UI activity card streams to the frontend in real time.
- Returns `(prelude_ran, is_fully_satisfied, tool_events_log, synthesized_response)` so deterministic
  desktop/demo commands finish in a single butter-smooth pass!
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from loguru import logger

from server.core.tool_repair import synthesize_butter_smooth_summary


_PAINT_SHAPES = (
    "circle",
    "square",
    "rectangle",
    "triangle",
    "star",
    "heart",
    "smiley",
    "spiral",
    "line",
    "house",
    "arrow",
    "diamond",
)

_APP_ALIASES = {
    "paint": "mspaint",
    "ms paint": "mspaint",
    "mspaint": "mspaint",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "spotify": "spotify",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "vs code": "code",
    "vscode": "code",
    "file explorer": "explorer",
    "explorer": "explorer",
    "terminal": "wt",
    "powershell": "powershell",
}


def plan_scripted_prelude_steps(user_message: str) -> Tuple[List[Tuple[str, Dict[str, Any]]], bool]:
    """
    Analyze `user_message` and return `(steps, is_complete_fast_path)`.
    If `steps` is non-empty, each item is `(tool_name, tool_kwargs)`.
    `is_complete_fast_path` is True when executing these steps completely fulfills the user's prompt
    without needing an additional multi-turn LLM loop.
    """
    raw = (user_message or "").strip()
    low = raw.lower()
    if not low:
        return [], False

    steps: List[Tuple[str, Dict[str, Any]]] = []

    # 1. MS Paint / Canvas Shape Drawing (handles single or multiple shapes, e.g. "open paint and draw a circle and a star")
    has_draw_verb = any(v in low for v in ("draw", "make", "sketch", "paint", "create a ", "plot a "))
    matched_shapes = [sh for sh in _PAINT_SHAPES if re.search(rf"\b{sh}s?\b", low)]
    if "face" in low and "smiley" not in matched_shapes:
        matched_shapes.append("smiley")

    if matched_shapes and (has_draw_verb or "paint" in low or "canvas" in low):
        n_shapes = len(matched_shapes)
        for idx, sh in enumerate(matched_shapes):
            offset_x = 0
            if n_shapes == 2:
                offset_x = 760 if idx == 0 else 1160
            elif n_shapes >= 3:
                offset_x = 660 + (idx * 300)
            steps.append((
                "computer_draw_shape",
                {
                    "shape": sh,
                    "center_x": offset_x,
                    "center_y": 0,
                    "radius": 130 if n_shapes == 1 else 100,
                    "app": "mspaint",
                },
            ))
        notepad_match = re.search(r"notepad\s+and\s+(?:write|type)\s+[\"']?([^\"'\n]+)[\"']?", raw, re.IGNORECASE)
        if notepad_match:
            steps.append(("launch_app", {"app": "notepad"}))
            steps.append(("computer_type", {"text": notepad_match.group(1).strip(), "press_enter": True}))
        return steps, True

    # 2. Open Notepad and type/write text: "open notepad and write/type ..."
    np_write = re.search(
        r"(?:open|launch|start|in)\s+notepad\s+(?:and\s+)?(?:write|type|enter|put)\s+[\"']?(.+?)[\"']?$",
        raw,
        re.IGNORECASE,
    )
    if np_write:
        text_to_type = np_write.group(1).strip()
        steps.append(("launch_app", {"app": "notepad"}))
        steps.append(("computer_type", {"text": text_to_type, "press_enter": True}))
        return steps, True

    # 3. Play YouTube Video: "play <query> on youtube" or "open youtube and play <query>"
    yt_match = (
        re.search(r"play\s+[\"']?(.+?)[\"']?\s+on\s+youtube", raw, re.IGNORECASE)
        or re.search(r"youtube\s+and\s+(?:play|search(?:\s+for)?)\s+[\"']?(.+?)[\"']?$", raw, re.IGNORECASE)
    )
    if yt_match:
        q = yt_match.group(1).strip()
        q = re.sub(r"\s+in\s+full\s*screen.*$", "", q, flags=re.IGNORECASE).strip()
        fullscreen = "fullscreen" in low or "full screen" in low
        steps.append(("play_youtube_video", {"query": q, "fullscreen": fullscreen}))
        return steps, True

    # 4. Hermes Programmatic Tool Calling (`execute_code`) demo prompt
    if "execute_code" in low and ("workspace" in low or "list" in low or "summarize" in low):
        demo_ptc_script = (
            "from hermes_tools import list_directory, json_parse\n"
            "import platform\n"
            "listing = list_directory('.')\n"
            "print('=== Hermes PTC Live Workspace Audit ===')\n"
            "print(f'Host OS: {platform.system()} {platform.release()} ({platform.machine()})')\n"
            "print(str(listing)[:900])\n"
        )
        steps.append(("execute_code", {"code": demo_ptc_script, "timeout": 30}))
        return steps, True

    # 5. Google Drive & Google Photos demo prompts
    has_drive = "google drive" in low or "my drive" in low
    has_photos = "google photos" in low or "my photos" in low or "recent photos" in low
    if (has_drive or has_photos) and any(v in low for v in ("search", "list", "show", "check", "recent", "files")):
        if has_drive:
            steps.append(("google_drive_search", {"query": "", "max_results": 8}))
        if has_photos:
            steps.append(("google_photos_list", {"page_size": 8}))
        if steps:
            return steps, True

    # 6. Simple standalone app launch: "open/launch/start paint/notepad/calculator/spotify/chrome/vscode"
    app_only = re.match(
        r"^(?:please\s+)?(?:can\s+you\s+)?(?:open|launch|start|focus)\s+(ms\s*paint|mspaint|paint|notepad|calculator|calc|spotify|google\s+chrome|chrome|microsoft\s+edge|edge|vs\s*code|vscode|file\s+explorer|explorer|terminal)\s*[.!]?$",
        low,
    )
    if app_only:
        app_key = re.sub(r"\s+", " ", app_only.group(1).strip())
        target_app = _APP_ALIASES.get(app_key, app_key)
        steps.append(("launch_app", {"app": target_app}))
        return steps, True

    # 7. Take a desktop screenshot / capture screen
    if re.match(r"^(?:please\s+)?(?:take|capture|grab|show)\s+(?:a\s+)?(?:desktop\s+)?(?:screenshot|screen\s*capture|screen)\s*[.!]?$", low):
        steps.append(("capture_screen", {}))
        return steps, True

    # 8. Check system info / hardware telemetry
    if re.search(r"\b(?:check|show|get|what\s+is)\s+(?:my\s+)?(?:system\s+info|hardware\s+info|cpu\s+and\s+ram|workstation\s+status)\b", low):
        steps.append(("system_info", {}))
        return steps, True

    return [], False


async def run_demo_scripted_prelude(
    user_message: str,
    callable_map: Dict[str, Callable],
) -> Tuple[bool, bool, List[Dict[str, Any]], str]:
    """
    Execute any deterministic scripted prelude steps using `callable_map` (the wrapped engine tools).
    Returns `(prelude_ran, is_complete_fast_path, tool_events_log, synthesized_summary)`.
    """
    steps, is_complete = plan_scripted_prelude_steps(user_message)
    if not steps:
        return False, False, [], ""

    tool_events_log: List[Dict[str, Any]] = []
    for tool_name, kwargs in steps:
        fn = callable_map.get(tool_name)
        if not fn:
            logger.debug(f"[ScriptedPrelude] Tool '{tool_name}' not in callable_map; skipping prelude step.")
            return False, False, [], ""
        try:
            logger.info(f"[ScriptedPrelude] Executing deterministic step: {tool_name}({kwargs})")
            res = await fn(**kwargs)
            tool_events_log.append({
                "tool": tool_name,
                "params": kwargs,
                "result": str(res),
            })
        except Exception as exc:
            logger.warning(f"[ScriptedPrelude] Step {tool_name} raised {exc}")
            tool_events_log.append({
                "tool": tool_name,
                "params": kwargs,
                "result": f"Error: {exc}",
            })

    summary = synthesize_butter_smooth_summary(user_message, tool_events_log)
    return True, is_complete, tool_events_log, summary
