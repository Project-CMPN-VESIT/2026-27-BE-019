import subprocess, os, sys

input_video = r"C:\Users\Jass\Videos\2026-11-20 21-30-34.mp4"
output_video = r"C:\Users\Jass\Videos\Dione_Commands_Demo_Clean_Cut.mp4"
repo_copy = r"C:\Users\Jass\Documents\CAPSTONE\PROJECT - I\docs\figures\Dione_Commands_Demo_Clean_Cut.mp4"

# Exact cut segments: (start_s, end_s, description)
segments = [
    (104.5, 115.5, "Segment 1: System Boot & 'hi dione' Greeting"),
    (161.5, 220.0, "Segment 2: Autonomous Web Intelligence & Gmail Dispatch"),
    (283.0, 304.5, "Segment 3: Real-World Verification (Live Gmail Sent Confirmation)"),
    (325.0, 373.0, "Segment 4: Live Workstation Telemetry & GPU Stats ('whats my pc stats?')"),
    (387.0, 395.0, "Segment 5A: CUA Input ('can you open paint and draw a circle')"),
    (411.8, 437.5, "Segment 5B: Win32 Paint Execution & Canvas Circle Draw"),
    (476.5, 484.5, "Segment 6A: Media Input ('can you play latest bollywood song')"),
    (557.5, 572.5, "Segment 6B: YouTube Autonomous Launch & Playback"),
    (591.5, 604.0, "Segment 6C: Media Execution Confirmation in Dione"),
    (615.0, 645.0, "Segment 7: Final Closing & Workstation Activity Audit Trail")
]

filter_parts = []
concat_v = []
concat_a = []

for idx, (st, en, desc) in enumerate(segments):
    print(f"[{idx+1}/{len(segments)}] {desc}: {st}s -> {en}s ({en-st:.1f}s)")
    # Crop top 44px to hide Windows taskbar, scale back to 1920x1080
    v_filter = f"[0:v]trim=start={st}:end={en},setpts=PTS-STARTPTS,crop=1920:1036:0:44,scale=1920:1080[v{idx}];"
    a_filter = f"[0:a]atrim=start={st}:end={en},asetpts=PTS-STARTPTS[a{idx}];"
    filter_parts.append(v_filter)
    filter_parts.append(a_filter)
    concat_v.append(f"[v{idx}]")
    concat_a.append(f"[a{idx}]")

# Build concat string
concat_pairs = "".join([f"{v}{a}" for v, a in zip(concat_v, concat_a)])
concat_filter = f"{concat_pairs}concat=n={len(segments)}:v=1:a=1[outv][outa]"
full_filter = "".join(filter_parts) + concat_filter

# Write filter complex to file to avoid command line length limits on Windows
filter_file = "scratch/filter_complex.txt"
with open(filter_file, "w", encoding="utf-8") as f:
    f.write(full_filter)

print("\nFilter complex written to scratch/filter_complex.txt")
total_duration = sum(en - st for st, en, _ in segments)
print(f"Total edited video runtime: {total_duration:.1f}s (~{total_duration/60:.2f} minutes)")

cmd = [
    "ffmpeg", "-y",
    "-i", input_video,
    "-filter_complex_script", filter_file,
    "-map", "[outv]",
    "-map", "[outa]",
    "-c:v", "h264_nvenc",
    "-preset", "p6",
    "-b:v", "10M",
    "-maxrate", "12M",
    "-bufsize", "20M",
    "-c:a", "aac",
    "-b:a", "192k",
    output_video
]

print("\nStarting hardware-accelerated NVENC render...")
res = subprocess.run(cmd, capture_output=True, text=True)

if res.returncode != 0:
    print("FFmpeg Error:")
    print(res.stderr[-1000:])
    sys.exit(1)

print(f"\nRender completed successfully! Output: {output_video}")

# Copy to repo docs/figures/
os.makedirs(os.path.dirname(repo_copy), exist_ok=True)
import shutil
shutil.copy2(output_video, repo_copy)
print(f"Copied to repo: {repo_copy}")
