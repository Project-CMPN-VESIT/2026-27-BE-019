import asyncio
import edge_tts
import subprocess
import os
import shutil

input_video = r"C:\Users\Jass\Downloads\Dione_AI_Capstone_Demo_v2.mp4"
output_video = r"C:\Users\Jass\Videos\Dione_AI_Capstone_Demo_v2_Voiceover.mp4"
downloads_copy = r"C:\Users\Jass\Downloads\Dione_AI_Capstone_Demo_v2_Voiceover.mp4"
temp_dir = r"scratch/vo_final"
os.makedirs(temp_dir, exist_ok=True)

script_items = [
    (0.0, "This is Dione AI, our local personal assistant."),
    (4.0, "Booting locally loads our knowledge graph, vector store, and five-tier Safety Kernel."),
    (10.0, "On localhost 8900, the Sovereign Workspace greets the user with saved context."),
    (16.0, "First, we ask Dione to research NVIDIA news and email Riya. The ReAct loop runs a live web search, formats the summary in JSON, and sends the email automatically."),
    (32.0, "Opening the sent email confirms live delivery, with the latest RTX 50 series and Hugging Face updates."),
    (42.0, "Next, asking for PC stats returns live CPU, RAM, disk, and RTX 3050 Ti GPU telemetry from Windows."),
    (51.0, "Now for desktop control. We ask Dione to open Paint and draw a circle. Our Win32 adapter launches MS Paint, draws the circle live, and logs the full code trace."),
    (68.0, "For media control, asking for the latest Bollywood song searches YouTube, opens the track in full screen, and logs each step in the activity panel."),
    (83.0, "Every action stays transparent, fast, and protected by our local safety layer."),
    (90.0, "One-millisecond graph lookup, 93% recall, and all tests passed. Thanks for watching.")
]

VOICE = "en-US-ChristopherNeural"

async def generate_audio():
    print("Generating studio neural audio clips...")
    for idx, (st, text) in enumerate(script_items):
        fpath = os.path.join(temp_dir, f"clip_{idx:02d}.mp3")
        comm = edge_tts.Communicate(text, VOICE, rate="+6%")
        await comm.save(fpath)
        print(f"[{idx+1}/10] Generated: {fpath}")

asyncio.run(generate_audio())

# Build ffmpeg audio filter to place each clip at its exact start time
# Using adelay and amix
inputs = ["-i", input_video]
filter_complex = []
for idx, (st, _) in enumerate(script_items):
    clip_path = os.path.join(temp_dir, f"clip_{idx:02d}.mp3").replace("\\", "/")
    inputs.extend(["-i", clip_path])
    delay_ms = int(st * 1000)
    # in ffmpeg 1-based index for additional audio inputs is idx + 1
    in_idx = idx + 1
    filter_complex.append(f"[{in_idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}];")

amix_inputs = "".join([f"[a{idx}]" for idx in range(len(script_items))])
filter_complex.append(f"{amix_inputs}amix=inputs={len(script_items)}:duration=longest:dropout_transition=0:normalize=0[vo];")
filter_complex.append("[vo]volume=1.8[final_a]")

full_filter = "".join(filter_complex)

filter_script = os.path.join(temp_dir, "audio_filter.txt")
with open(filter_script, "w", encoding="utf-8") as f:
    f.write(full_filter)

print("Muxing audio with video...")
cmd = [
    "ffmpeg", "-y",
    *inputs,
    "-filter_complex_script", filter_script,
    "-map", "0:v:0",
    "-map", "[final_a]",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    output_video
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFmpeg error:")
    print(res.stderr[-1000:])
    exit(1)

shutil.copy2(output_video, downloads_copy)
print("SUCCESS!")
print(f"Output saved to: {output_video}")
print(f"Copy saved to: {downloads_copy}")
