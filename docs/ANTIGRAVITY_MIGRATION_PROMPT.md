# Antigravity Master Migration & Hermes + OpenClaw Integration Prompt for Dione Autonomous Agent (v7.0 Butter-Smooth Live Demo Edition)

Copy and paste the entire block below into **Antigravity** (alongside the extracted `dione-autonomous-agent-upgraded.zip` workspace) so it applies and verifies every module ported from **`hermes-agent-main.zip`** ([NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent)), **`openclaw-clean.zip`** ([openclaw/openclaw](https://github.com/openclaw/openclaw)), **`vercel-labs/agent-desktop`**, **`suitedaces/computer-agent`**, and **`qwenlm/open-computer-use`** without breaking project integrity:

````markdown
You are upgrading and maintaining the `dione-autonomous-agent` repository (v7.0 NousResearch Hermes Agent + OpenClaw + Butter-Smooth Professor Demo Edition).

## STRICT INTEGRITY & NON-DESTRUCTION RULES
1. **DO NOT** delete or overwrite `data/`, `.env`, `credentials.json`, `data/google_oauth_token.json`, or the native CUA binaries (`cua-driver.exe`, `cua-driver-uia.exe`, `cua_driver_sdk.dll`, `server/bin/nircmd.exe`).
2. **KEEP** `re`, `urllib.parse`, `math`, and `json` as top-level module imports in `server/plugins/builtin/system.py`, `server/plugins/builtin/computer_use_plugin.py`, and `server/plugins/builtin/hermes_execution_plugin.py`.
3. **DO NOT** re-introduce `**kwargs` into `@dione_tool`-decorated functions in `server/plugins/builtin/computer_use_plugin.py` or `server/plugins/builtin/hermes_execution_plugin.py`.
4. **KEEP** both `client/dist/assets/index-Dfd4O8id.js` and `client/dist/assets/index-B_sxjnyR.js` synchronized, as `client/dist/index.html` loads `/assets/index-Dfd4O8id.js`.

---

## 1. WHAT WAS PORTED FROM `hermes-agent-main.zip` & `openclaw-clean.zip`

### A. `server/core/scripted_prelude.py` — Hermes Scripted Prelude (`agent/turn_scripted_prelude.py`)
- Executes unambiguous single and multi-step live-demo commands **before** the first model call directly through `DioneEngine`'s wrapped tool callables (`ACTING` -> `OBSERVING` + live desktop screenshot capture), eliminating LLM hesitation, redundant tool calls, and 429 rate-limit stalls:
  1. **MS Paint Single & Multi-Shape Studio**: `"Open Paint and draw a circle"`, `"draw a star and a heart"`, `"draw a house"`, `"draw a smiley face"`, `"draw a square / triangle / diamond / arrow / spiral"` (auto-offsets `center_x` when multiple shapes are requested in one prompt).
  2. **Notepad + Live Typing**: `"Open Notepad and write ..."` -> runs `launch_app(app="notepad")` + `computer_type(text=..., press_enter=True)`.
  3. **Hermes Programmatic Tool Calling (`execute_code`)**: `"Use execute_code to list the workspace directory and summarize core modules"` -> executes a live Python script in the PTC sandbox over the `127.0.0.1` loopback RPC bridge.
  4. **Google Drive & Google Photos**: `"Search my Google Drive files and list my recent Google Photos"` -> runs `google_drive_search` + `google_photos_list` (with 3-tier OAuth2 -> Local Drive/Pictures -> Local Mirror fallback).
  5. **YouTube Media Playback, App Launch, Screenshots & System Info**: `"Play ... on YouTube"`, `"Open Calculator/Spotify/Chrome/VS Code"`, `"Take a screenshot"`, `"Check my system info"`.

### B. `server/core/tool_repair.py` — Hermes `arg_coercion.py` + OpenClaw `@openclaw/tool-call-repair`
- **`coerce_tool_args_for_callable`**: Repairs string-typed integers (`"130"` -> `130`), floats, booleans (`"true"` -> `True`), and JSON-encoded lists/dicts, and maps alias parameter names (`app_name` -> `app`, `filepath` -> `path`, `cmd` -> `command`) while stripping unknown kwargs so tool calls never fail with `TypeError`.
- **`detect_and_repair_plaintext_tool_calls`**: Detects standalone JSON or `[tool:name]{...}` tool calls emitted in plain text and executes the real tool automatically.
- **`scrub_repetitive_output` & `synthesize_butter_smooth_summary`**: Truncates repetition loops (`agent/repetition_guard.py`) and guarantees a rich Jarvis-style markdown summary even if the LLM returns empty text or hits a quota limit after tool execution (`agent/empty_response_guard.py`).

### C. `server/plugins/builtin/computer_use_plugin.py` — Safe Canvas Clamping & 12 Shape Primitives
- Guards against Gemini passing `center_x=0, center_y=0` by clamping `cx, cy` strictly inside the detected MS Paint canvas bounds below the 170px Ribbon (`cx = max(c_left + 80, min(cx, c_right - 80))`).
- Supports 12 shapes: `circle`, `square`, `rectangle`, `triangle`, `star`, `heart`, `smiley`, `spiral`, `line`, `house`, `diamond`, and `arrow`.

### D. `client/dist/` & `client/src/` — OpenClaw Glass UI + Hermes `⚡ Live Demo Deck`
- Upgraded **both** `client/dist/assets/index-Dfd4O8id.js` (loaded by `index.html`) and `index-B_sxjnyR.js`, plus `index-ClaMBHeh.css`:
  - **OpenClaw Two-Tier Frosted Glass**: Deep charcoal base (`#0e1015`), `backdrop-filter: blur(12px) saturate(1.6)` header chrome, and ambient radial lighting.
  - **1-Click `⚡ Live Demo Deck` Bar**: Persistent pill bar right above the Composer (`🎨 Paint Circle`, `⭐ Paint Star & Heart`, `🏠 Paint House`, `📝 Notepad Note`, `🐍 Hermes PTC Code`, `☁️ Drive & Photos`, `▶️ YouTube Lofi`, `🖥️ System Info`) plus 4 interactive hero cards on new sessions.
  - **Hermes `ToolLabel` Badges (`cn`)**: Crisp `app · action` badges for `computer_draw_shape`, `computer_drag`, `computer_uia_action`, `execute_code`, `todo`, and `delegate_task`.
  - **Zero `"Thinking..."` Hang**: `onRunFinished` automatically populates a markdown summary if `content` is empty and refreshes the live desktop screenshot (`Ce()`).

---

## 2. VERIFICATION COMMANDS FOR ANTIGRAVITY
Run these verification checks from the project root after placing all files:
```bash
python -m py_compile server/core/engine.py server/core/tool_repair.py server/core/scripted_prelude.py server/core/goal_verifier.py server/core/runtime/computer_use.py server/plugins/builtin/hermes_execution_plugin.py server/plugins/builtin/computer_use_plugin.py server/plugins/builtin/system.py server/plugins/integrations/google_oauth.py server/plugins/integrations/google_drive.py server/plugins/integrations/google_photos.py
node --check client/dist/assets/index-Dfd4O8id.js
```
````