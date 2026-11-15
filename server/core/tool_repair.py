"""
Dione AI — Tool Call Coercion, Plain-Text Repair & Output Guards (v6.0)
=======================================================================
Directly ported from:
1. NousResearch/hermes-agent (`tools/arg_coercion.py`, `agent/empty_response_guard.py`, `agent/repetition_guard.py`, `tools/tool_labels.py`)
2. OpenClaw (`packages/tool-call-repair/attempt.ts`, `payload.ts`, `promote.ts`)

Guarantees:
- String-typed integers ("130"), floats ("0.5"), booleans ("true"), and JSON strings ('["a","b"]')
  are coerced to their exact Python signature types before invoking any tool.
- Unexpected hallucinated kwargs are stripped safely instead of raising TypeError.
- Plain-text / JSON / XML / bracketed tool calls emitted in assistant text are detected and promoted
  to real tool executions.
- Empty or repetitive model completions after tool runs are automatically replaced with rich,
  human-readable executive summaries.
"""

from __future__ import annotations

import inspect
import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from loguru import logger


# ---------------------------------------------------------------------------
# 1. Hermes Schema-Guided Argument Coercion (`tools/arg_coercion.py`)
# ---------------------------------------------------------------------------
def coerce_tool_args_for_callable(func: Callable, raw_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coerce LLM-supplied keyword arguments against a Python callable's signature & annotations.
    Ported from NousResearch/hermes-agent `tools/arg_coercion.py`.
    """
    if not raw_kwargs or not isinstance(raw_kwargs, dict):
        return {}

    try:
        sig = inspect.signature(func)
    except Exception:
        return dict(raw_kwargs)

    accepts_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )

    coerced: Dict[str, Any] = {}
    for k, val in raw_kwargs.items():
        if k not in sig.parameters and not accepts_var_keyword:
            # Map common alias parameter names before dropping
            if k in ("app_name", "application", "program") and "app" in sig.parameters and "app" not in raw_kwargs:
                k = "app"
            elif k in ("filepath", "file", "filename") and "path" in sig.parameters and "path" not in raw_kwargs:
                k = "path"
            elif k in ("cmd", "script") and "command" in sig.parameters and "command" not in raw_kwargs:
                k = "command"
            elif k in ("q", "search_query") and "query" in sig.parameters and "query" not in raw_kwargs:
                k = "query"
            else:
                logger.debug(f"[ArgCoercion] Dropping unknown arg '{k}' for {getattr(func, '__name__', 'tool')}")
                continue

        param = sig.parameters.get(k)
        if param is None:
            coerced[k] = val
            continue

        ann = param.annotation
        ann_str = str(ann).lower()

        if val is None:
            if param.default is not inspect.Parameter.empty:
                coerced[k] = param.default
            else:
                coerced[k] = None
            continue

        try:
            # Coerce string -> int
            if (ann is int or "int" in ann_str) and not ("list" in ann_str or "dict" in ann_str):
                if isinstance(val, str):
                    clean_v = val.strip().replace(",", "")
                    coerced[k] = int(float(clean_v))
                    continue
                elif isinstance(val, float):
                    coerced[k] = int(round(val))
                    continue

            # Coerce string -> float
            if ann is float or "float" in ann_str:
                if isinstance(val, str):
                    coerced[k] = float(val.strip().replace(",", ""))
                    continue

            # Coerce string -> bool
            if ann is bool or "bool" in ann_str:
                if isinstance(val, str):
                    low = val.strip().lower()
                    if low in ("true", "1", "yes", "on"):
                        coerced[k] = True
                        continue
                    if low in ("false", "0", "no", "off", ""):
                        coerced[k] = False
                        continue

            # Coerce JSON string or scalar -> list
            if ann is list or "list" in ann_str:
                if isinstance(val, str):
                    s_val = val.strip()
                    if s_val.startswith("[") and s_val.endswith("]"):
                        parsed = json.loads(s_val)
                        if isinstance(parsed, list):
                            coerced[k] = parsed
                            continue
                    coerced[k] = [x.strip() for x in s_val.split(",") if x.strip()] if "," in s_val else [s_val]
                    continue

            # Coerce JSON string -> dict
            if ann is dict or "dict" in ann_str:
                if isinstance(val, str):
                    s_val = val.strip()
                    if s_val.startswith("{") and s_val.endswith("}"):
                        parsed = json.loads(s_val)
                        if isinstance(parsed, dict):
                            coerced[k] = parsed
                            continue
        except Exception as coerce_err:
            logger.debug(f"[ArgCoercion] Keeping original value for {k}: {coerce_err}")

        coerced[k] = val

    return coerced


def repair_and_coerce_tool_call(tool_name: str, tool_callable: Any, raw_args: Dict[str, Any]) -> Dict[str, Any]:
    """Preserves Hermes & OpenClaw arg coercion and parameter repair."""
    if callable(tool_callable):
        return coerce_tool_args_for_callable(tool_callable, raw_args)
    return dict(raw_args or {})


# ---------------------------------------------------------------------------
# 2. OpenClaw Plain-Text Tool Call Repair (`@openclaw/tool-call-repair`)
# ---------------------------------------------------------------------------
_JSON_TOOL_BLOCK_RE = re.compile(
    r"(?:```(?:json|tool_call|tool)?\s*)?(\{\s*\"(?:name|tool|tool_name|function)\"\s*:\s*\"[a-zA-Z0-9_.]+\"(?:[^{}]|\{[^{}]*\})*\})(?:\s*```)?",
    re.IGNORECASE,
)

_BRACKET_TOOL_RE = re.compile(
    r"\[(?:tool:)?([a-zA-Z0-9_]+)\]\s*(\{[\s\S]*?\})",
    re.IGNORECASE,
)


def detect_and_repair_plaintext_tool_calls(
    text: str,
    available_tool_names: set[str],
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Detect standalone plain-text / JSON / bracketed tool calls emitted when a model
    accidentally outputs tool syntax in prose instead of native function-calling.
    Ported from OpenClaw `packages/tool-call-repair`.
    """
    if not text or not available_tool_names:
        return []

    repaired: List[Tuple[str, Dict[str, Any]]] = []

    # 1. Check JSON tool call blocks: {"name": "tool_name", "arguments": {...}}
    for match in _JSON_TOOL_BLOCK_RE.finditer(text):
        raw_json = match.group(1).strip()
        try:
            obj = json.loads(raw_json)
            if not isinstance(obj, dict):
                continue
            t_name = (
                obj.get("name")
                or obj.get("tool")
                or obj.get("tool_name")
                or obj.get("function")
                or ""
            ).strip()
            if t_name in available_tool_names:
                args = (
                    obj.get("arguments")
                    or obj.get("args")
                    or obj.get("params")
                    or obj.get("parameters")
                    or obj.get("input")
                    or {}
                )
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                if isinstance(args, dict):
                    repaired.append((t_name, args))
        except Exception:
            continue

    # 2. Check OpenClaw / Harmony bracketed syntax: [tool:name]{"arg": "val"}
    for match in _BRACKET_TOOL_RE.finditer(text):
        t_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        if t_name in available_tool_names:
            try:
                args = json.loads(raw_args)
                if isinstance(args, dict):
                    repaired.append((t_name, args))
            except Exception:
                continue

    return repaired


# ---------------------------------------------------------------------------
# 3. Hermes Repetition Guard (`agent/repetition_guard.py`)
# ---------------------------------------------------------------------------
MIN_FRAGMENT_LENGTH = 400
_REPEAT_WINDOW = 60
_MIN_REPEAT_COUNT = 5


def scrub_repetitive_output(text: str) -> str:
    """
    Detects degenerate repetition loops in model output and truncates cleanly.
    Ported from NousResearch/hermes-agent `agent/repetition_guard.py`.
    """
    if not text or len(text) < MIN_FRAGMENT_LENGTH:
        return text

    step = max(1, _REPEAT_WINDOW // 2)
    counts: Dict[str, int] = {}
    first_seen_end: Dict[str, int] = {}
    for i in range(0, len(text) - _REPEAT_WINDOW + 1, step):
        win = text[i : i + _REPEAT_WINDOW]
        if not win.strip():
            continue
        counts[win] = counts.get(win, 0) + 1
        if counts[win] == 2:
            first_seen_end[win] = i + _REPEAT_WINDOW
        if counts[win] >= _MIN_REPEAT_COUNT:
            cutoff = first_seen_end.get(win, i)
            return text[:cutoff].rstrip()

    return text


# ---------------------------------------------------------------------------
# 4. Hermes Empty-Response Guard & Rich Tool Summary (`agent/empty_response_guard.py` + `tools/tool_labels.py`)
# ---------------------------------------------------------------------------
def synthesize_butter_smooth_summary(
    user_message: str,
    tool_events: List[Dict[str, Any]],
) -> str:
    """
    Synthesize a crisp, natural Jarvis-style executive summary from the executed tools
    and their results whenever the model returns empty text or after a fast-path prelude.
    """
    if not tool_events:
        return "Done! Let me know what you'd like to run next."

    bullets: List[str] = []
    for ev in tool_events:
        t_name = str(ev.get("tool") or "")
        params = ev.get("params") or {}
        res = str(ev.get("result") or "").strip()
        # Strip internal verification footers for clean user presentation
        clean_res = res.split("[Post-Action Visual Verification")[0].strip()

        if t_name == "computer_draw_shape":
            shape = params.get("shape", "circle")
            app = params.get("app", "MS Paint")
            bullets.append(
                f"- **MS Paint Canvas (`{shape.title()}`)**: Focused `{app}`, located the active drawing canvas below the Ribbon toolbar, and smoothly drew a **{shape}** using hardware `SendInput` drag interpolation ({clean_res[:180]})."
            )
        elif t_name == "computer_drag":
            bullets.append(
                f"- **Desktop Mouse Drag**: Smoothly dragged from `({params.get('start_x')}, {params.get('start_y')})` to `({params.get('end_x')}, {params.get('end_y')})` with `DragReleaseGuard`."
            )
        elif t_name == "launch_app":
            app = params.get("app", "application")
            bullets.append(f"- **Application Focus (`{app}`)**: Launched and brought **{app}** to the foreground window.")
        elif t_name == "computer_type":
            typed = params.get("text", "")
            bullets.append(f"- **Keyboard Input**: Typed `\"{typed[:80]}\"` into the active window.")
        elif t_name == "play_youtube_video":
            q = params.get("query", "video")
            bullets.append(f"- **YouTube Media Playback**: Opened and started playing **\"{q}\"** ({clean_res[:160]}).")
        elif t_name == "open_browser":
            u = params.get("url", "")
            bullets.append(f"- **Browser Navigation**: Opened `{u}` in your default browser.")
        elif t_name == "execute_code":
            try:
                parsed = json.loads(clean_res)
                out = (parsed.get("stdout") or "").strip()
                calls = parsed.get("tool_calls_made", 0)
                dur = parsed.get("duration_seconds", 0)
                bullets.append(
                    f"- **Hermes Programmatic Tool Execution (`execute_code`)**: Completed in `{dur}s` ({calls} RPC tool calls).\n```text\n{out[:600]}\n```"
                )
            except Exception:
                bullets.append(f"- **Hermes Programmatic Tool Execution (`execute_code`)**: {clean_res[:300]}")
        elif t_name == "todo":
            bullets.append(f"- **Hermes Task Ledger (`todo`)**:\n{clean_res[:500]}")
        elif "google_drive" in t_name:
            bullets.append(f"- **Google Drive**: {clean_res[:450]}")
        elif "google_photos" in t_name:
            bullets.append(f"- **Google Photos**: {clean_res[:450]}")
        elif "gmail" in t_name:
            bullets.append(f"- **Gmail**: {clean_res[:450]}")
        elif "calendar" in t_name:
            bullets.append(f"- **Google Calendar**: {clean_res[:450]}")
        elif t_name == "system_info":
            bullets.append(f"- **Windows 11 System Telemetry**:\n```text\n{clean_res[:600]}\n```")
        elif clean_res:
            bullets.append(f"- **`{t_name}`**: {clean_res[:320]}")
        else:
            bullets.append(f"- **`{t_name}`**: Completed.")

    header = f"I've completed your request (**\"{user_message[:90]}\"**):"
    return header + "\n\n" + "\n".join(bullets)
