import subprocess, os, sys

input_path = r"C:\Users\Jass\Videos\2026-11-20 21-30-34.mp4"
output_path = r"C:\Users\Jass\Videos\2026-11-20 21-30-34_under100mb.mp4"
friendly_copy = r"C:\Users\Jass\Videos\Dione_Full_Demo_Under100MB.mp4"

print(f"Compressing full original video: {input_path}")
print("Target: Under 100 MB with full 1080p resolution and complete 11m 12s duration.")

# Using libx264 with CRF 23, capped maxrate 1100k
cmd = [
    "ffmpeg", "-y",
    "-i", input_path,
    "-c:v", "libx264",
    "-crf", "23",
    "-preset", "veryfast",
    "-maxrate", "1100k",
    "-bufsize", "2200k",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "64k",
    "-movflags", "+faststart",
    output_path
]

res = subprocess.run(cmd, capture_output=True, text=True)

if res.returncode != 0:
    print("Error during compression:")
    print(res.stderr[-1000:])
    sys.exit(1)

file_size_bytes = os.path.getsize(output_path)
file_size_mb = file_size_bytes / (1024 * 1024)

print(f"\nCompression complete!")
print(f"Output File: {output_path}")
print(f"Final File Size: {file_size_mb:.2f} MB")

if file_size_mb < 100.0:
    print(f"SUCCESS: {file_size_mb:.2f} MB is strictly UNDER the 100 MB threshold!")
else:
    print(f"WARNING: File size {file_size_mb:.2f} MB exceeded 100 MB.")

# Copy friendly name
import shutil
shutil.copy2(output_path, friendly_copy)
print(f"Saved copy to: {friendly_copy}")
