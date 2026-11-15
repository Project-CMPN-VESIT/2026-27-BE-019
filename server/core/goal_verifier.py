"""
Dione AI — Closed-Loop Visual Goal Verifier & Reflection Engine (v5.0 Open-CUA Edition)
=======================================================================================
Empirically inspects desktop screenshots, foreground window metadata, pre/post frame change,
and active multi-step sub-goals to verify if the user's complete intent was achieved on screen.

CRITICAL DESIGN RULE (Anti-Premature-Stop & Anti-Hang):
- Never report `ACHIEVED` after a mere preparatory step (`launch_app`, `capture_screen`,
  `list_open_windows`, `inspect_screen_vision`, `focus_app`) when the user's prompt also
  requests an in-app interaction (such as drawing a shape in Paint, clicking a button,
  queuing into a match, typing text, searching, or playing media).
- Immediately report `ACHIEVED` once the target interactive tool (`computer_draw_shape`,
  `computer_drag`, `computer_locate_and_click`, `computer_click`, `computer_type`, etc.)
  succeeds on the target window, preventing endless post-completion loops.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


# Preparatory / observation-only tools that NEVER satisfy a multi-step interactive command by themselves
OBSERVATION_OR_PREP_TOOLS = {
    "capture_screen",
    "list_open_windows",
    "inspect_screen_vision",
    "launch_app",
}

# Physical interaction tools that actually draw, drag, click, type, or invoke controls inside a target window
INTERACTIVE_INPUT_TOOLS = {
    "computer_draw_shape",
    "computer_drag",
    "computer_uia_action",
    "computer_locate_and_click",
    "computer_click",
    "computer_type",
    "computer_hotkey",
    "play_youtube_video",
}

# Refusal / delegation cop-out phrases that must NEVER be accepted as a final answer
STUBBORN_REFUSAL_PATTERNS = [
    r"one\s+click\s+away",
    r"just\s+one\s+click",
    r"you\s+can\s+(?:now\s+)?(?:hit|click|press)\s+play",
    r"feel\s+free\s+to\s+(?:click|hit|press)",
    r"runs\s+directly\s+inside\s+the\s+game\s+client\s+engine",
    r"custom\s+directx",
    r"anti[\s-]?cheat\s+prevents",
    r"cannot\s+click\s+inside",
    r"please\s+click\s+the\s+.*?\s+button\s+yourself",
    r"you\s+may\s+now\s+click",
    r"go\s+ahead\s+and\s+(?:click|press|hit)",
]


def detect_stubborn_refusal_or_delegation(response_text: str) -> Tuple[bool, str]:
    """
    Checks if the model's text response tries to delegate the final physical click/action
    back to the user or makes excuses about game engines/DirectX/overlays.
    """
    if not response_text:
        return False, ""
    text_low = response_text.lower()
    for pat in STUBBORN_REFUSAL_PATTERNS:
        m = re.search(pat, text_low)
        if m:
            return (
                True,
                f"Detected prohibited delegation/refusal phrase ('{m.group(0)}'). "
                "You are strictly forbidden from telling the user they are 'one click away' or asking them to click Play/buttons themselves.",
            )
    return False, ""


def prompt_requires_in_app_interaction(user_prompt: str) -> Tuple[bool, str]:
    """
    Determines whether the user prompt requires an active in-window action BEYOND merely
    launching or focusing an application window.
    Returns (requires_interaction, required_action_summary).
    """
    p = user_prompt.lower().strip()

    # 1. Drawing / MS Paint / Canvas shapes
    for shape_kw in ("circle", "square", "rectangle", "triangle", "star", "heart", "smiley", "spiral", "oval"):
        if shape_kw in p and any(v in p for v in ("draw", "make", "paint", "sketch", "create")):
            return (
                True,
                f"Call `computer_draw_shape(shape='{shape_kw}', app='mspaint')` right now to draw the {shape_kw} directly on the Paint canvas.",
            )
    if any(k in p for k in ("draw ", "sketch ", "paint a ")):
        return (
            True,
            "Call `computer_draw_shape(shape='circle', app='mspaint')` or `computer_drag(start_x=..., start_y=..., end_x=..., end_y=...)` to draw on the canvas.",
        )

    # 2. Drag and drop
    if "drag" in p:
        return (
            True,
            "Call `computer_drag(start_x=..., start_y=..., end_x=..., end_y=...)` to perform the mouse drag.",
        )

    # 3. Queue / Matchmaking / Game start patterns
    if any(k in p for k in ("queue", "deathmatch", "matchmaking", "start match", "find match", "hit play", "click play", "play valorant", "start game", "comp", "unrated", "swiftplay")):
        return (
            True,
            "Visually locate and click the mode selection / 'Play' / 'Start' / 'Queue' button inside the game or Riot Client using `computer_locate_and_click` or `inspect_screen_vision` + `computer_click`.",
        )

    # 4. Explicit click requests
    click_m = re.search(r"\b(?:click|press|tap|select|hit)\s+(?:on\s+)?(?:the\s+)?([a-z0-9 _\-'\"]{2,35})", p)
    if click_m:
        target = click_m.group(1).strip()
        return True, f"Execute the click on '{target}' using `computer_locate_and_click(description='{target}')` or `computer_click`."

    # 5. Explicit typing / writing into an app
    if any(k in p for k in ("type ", "write ", "enter text", "paste ", "search for ", "calculate ", "compute ")):
        return True, "Focus the target input area and enter the requested text/calculation using `computer_type(text=..., press_enter=True)` or `computer_hotkey`."

    return False, ""


def verify_goal_on_desktop(
    user_prompt: str,
    tool_name: str,
    tool_params: Dict[str, Any],
    tool_result: str,
    audit_data: Dict[str, Any],
    executed_tools_history: List[str] | None = None,
) -> Tuple[bool, str, str]:
    """
    Evaluates whether the user's COMPLETE intended goal was achieved based on
    the post-action desktop capture, active window metadata, and the full sequence
    of tools executed in the current turn.

    Returns:
        (is_achieved: bool, reflection_issue: str, corrective_advice: str)
    """
    prompt_low = user_prompt.lower().strip()
    win = audit_data.get("window", {})
    win_title = win.get("title", "")
    win_title_low = win_title.lower()
    is_fs = win.get("is_fullscreen", False)
    history = executed_tools_history or [tool_name]

    # 0. Fast-path success when computer_draw_shape or auto-routed drawing completed
    res_low = (tool_result or "").lower()
    if "successfully drew" in res_low:
        return True, "", ""

    # 0.1 Check if tool itself reported failure or inability to locate element
    if any(err in res_low for err in ("could not locate", "could not launch", "error:", "failed to execute", '"ok": false')):
        return (
            False,
            f"Tool `{tool_name}` reported an incomplete or failed outcome: {tool_result[:200]}",
            "Call `inspect_screen_vision` to see the exact current screen layout and coordinates, then click/drag the target using `computer_click`, `computer_drag`, or `computer_draw_shape`.",
        )

    # 1. Verification for Video / YouTube / Full-Screen Playback
    wants_video = any(k in prompt_low for k in ("video", "youtube", "watch", "mkbhd", "mrwhosetheboss", "veritasium", "song", "music video"))
    wants_fullscreen = any(k in prompt_low for k in ("full screen", "fullscreen", "full-screen", "kiosk", "f11"))

    if wants_video:
        raw_target_str = (str(tool_params) + " " + str(tool_result)).lower()
        if any(sq in raw_target_str for sq in ("/results", "search_query", "search?")) and "watch?v=" not in raw_target_str:
            return (
                False,
                "A YouTube search results URL was opened instead of playing a direct video watch URL (/watch?v=...).",
                "Call `play_youtube_video(query=..., fullscreen=True)` to resolve and launch the direct `/watch?v=...` video URL.",
            )

        if ("search" in win_title_low or "results" in win_title_low) and "watch" not in win_title_low:
            return (
                False,
                f"Active window '{win_title}' is showing YouTube search results rather than a playing video.",
                "Click the top video title using `computer_locate_and_click` or call `play_youtube_video` to open the direct watch URL.",
            )

        has_browser_in_title = any(b in win_title_low for b in ("youtube", "edge", "chrome", "firefox", "brave", "video"))
        if not has_browser_in_title and win_title_low not in ("", "unknown window", "desktop / background worker"):
            return (
                False,
                f"No video playback or browser window is in the foreground. Active window is '{win_title}'.",
                "Bring the browser window to the foreground using `launch_app('chrome')` or `play_youtube_video`.",
            )

        if wants_fullscreen and not is_fs:
            return (
                False,
                f"The video window '{win_title}' is not yet in fullscreen mode.",
                "Press 'f' or 'f11' via `computer_hotkey(keys='f')` to enter fullscreen playback.",
            )

        return True, "", ""

    # 2. Verification for Standalone Full Screen Request
    if wants_fullscreen and not wants_video:
        if not is_fs:
            return (
                False,
                f"Active window '{win_title}' is not in full screen mode.",
                "Send 'f11' via `computer_hotkey(keys='f11')` to toggle full screen on the active window.",
            )
        return True, "", ""

    # 3. Verification for Application Launching / Window Focusing + In-App Multi-Step Actions
    app_keywords = {
        "paint": ["paint", "mspaint"],
        "mspaint": ["paint", "mspaint"],
        "notepad": ["notepad", "untitled"],
        "calculator": ["calc", "calculator"],
        "chrome": ["chrome", "google chrome"],
        "edge": ["edge", "microsoft edge"],
        "code": ["visual studio code", "vs code", "code"],
        "explorer": ["file explorer", "explorer", "this pc"],
        "spotify": ["spotify"],
        "terminal": ["powershell", "cmd", "terminal", "command prompt"],
        "valorant": ["valorant", "riot client", "riot"],
        "riot": ["riot client", "valorant", "riot"],
        "discord": ["discord"],
        "steam": ["steam"],
    }

    matched_app = None
    for app_name, match_tokens in app_keywords.items():
        if re.search(r"\b" + re.escape(app_name) + r"\b", prompt_low):
            matched_app = (app_name, match_tokens)
            break

    if matched_app:
        app_name, match_tokens = matched_app
        if win_title_low not in ("", "unknown window", "desktop / background worker") and not any(token in win_title_low for token in match_tokens):
            return (
                False,
                f"Target application '{app_name}' is not in the foreground yet. Current foreground window is '{win_title}'.",
                f"Call `launch_app(app='{app_name}')` or `computer_draw_shape(app='{app_name}')` to bring '{app_name}' to the foreground.",
            )

    # 4. Multi-Step In-App Interaction Gate (CRITICAL: Prevents stopping after launch_app / capture_screen!)
    needs_interaction, interaction_advice = prompt_requires_in_app_interaction(user_prompt)
    if needs_interaction:
        has_performed_interactive_input = any(
            t in INTERACTIVE_INPUT_TOOLS
            or (t == "computer_use" and str(tool_params.get("action", "")).lower() in ("click", "double_click", "right_click", "drag", "draw_circle", "type", "key"))
            or ("successfully drew" in res_low)
            or ("dragged mouse" in res_low)
            for t in history
        )
        if not has_performed_interactive_input:
            return (
                False,
                f"You have only performed preparatory/focus actions ({history}), but you have NOT yet executed the requested in-app action for: '{user_prompt}'.",
                f"DO NOT STOP HERE! {interaction_advice}",
            )

    # 5. Command / CLI Execution Verification
    if tool_name in ("run_command", "cmd", "powershell", "execute_script"):
        if any(err_sig in res_low for err_sig in ("failed to execute", "command failed", "error: ", "exit code: 1", "syntax error")):
            return (
                False,
                f"CLI command failed with execution error: {tool_result[:160]}",
                "Analyze the error message, correct the command flags/syntax, and retry execution.",
            )

    return True, "", ""
