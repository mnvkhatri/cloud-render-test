import os
import sys
import time
import asyncio
import subprocess
import edge_tts
from playwright.async_api import async_playwright

WIDTH = 1080
HEIGHT = 1920
FPS = 24
OUTPUT_VIDEO = "render_action_test.mp4"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 0;
    width: 1080px;
    height: 1920px;
    background: radial-gradient(circle at 50% 30%, #1a0933, #05010a);
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans Devanagari', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }
  .card {
    width: 900px;
    height: 1200px;
    background: rgba(255, 255, 255, 0.05);
    border: 3px solid #ffd700;
    border-radius: 40px;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.3);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px;
    box-sizing: border-box;
    text-align: center;
    backdrop-filter: blur(20px);
  }
  .badge {
    background: linear-gradient(90deg, #ff8c00, #ff0080);
    padding: 16px 40px;
    border-radius: 50px;
    font-size: 36px;
    font-weight: bold;
    margin-bottom: 40px;
    letter-spacing: 2px;
  }
  h1 {
    font-size: 64px;
    margin: 20px 0;
    color: #fff;
    line-height: 1.3;
  }
  .highlight {
    color: #ffd700;
  }
  .sub {
    font-size: 38px;
    color: #d1d5db;
    margin-top: 40px;
    line-height: 1.4;
  }
  .timer {
    margin-top: 50px;
    font-size: 44px;
    font-family: monospace;
    color: #00ffcc;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="badge">🚀 GITHUB ACTIONS CLOUD RENDER</div>
    <h1>समुद्र की गहराइयों में छुपा <span class="highlight">द्वारका का रहस्य!</span></h1>
    <div class="sub">Zero-Server Cloud Render Test<br>Testing 1080p 60fps & Hindi Fonts</div>
    <div class="timer" id="time-display">Frame 0</div>
  </div>
  <script>
    function updateProgress(frameNum, totalFrames) {
      document.getElementById('time-display').innerText = 'Frame ' + frameNum + ' / ' + totalFrames;
      const card = document.querySelector('.card');
      const scale = 1 + 0.04 * Math.sin(frameNum / 12);
      card.style.transform = 'scale(' + scale + ')';
    }
  </script>
</body>
</html>
"""

async def generate_audio():
    print("🎙️ Generating Hindi TTS with edge-tts...")
    text = "समुद्र की गहराइयों में छुपा है पांच हज़ार साल पुराना सच। भगवान कृष्ण की द्वारका नगरी का यह रहस्य आपको हैरान कर देगा।"
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save("audio.mp3")
    print("✅ audio.mp3 generated successfully.")

def get_audio_duration():
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", "audio.mp3"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

async def capture_frames(total_frames):
    os.makedirs("frames", exist_ok=True)
    with open("index.html", "w") as f:
        f.write(HTML_TEMPLATE)

    print(f"🎬 Capturing {total_frames} frames ({WIDTH}x{HEIGHT} @ {FPS}fps) with Chromium...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        await page.goto(f"file://{os.path.abspath('index.html')}")
        await page.wait_for_load_state("networkidle")

        for f in range(total_frames):
            await page.evaluate(f"updateProgress({f+1}, {total_frames})")
            frame_path = f"frames/frame_{f:04d}.jpg"
            await page.screenshot(path=frame_path, quality=92, type="jpeg")
            if (f + 1) % 48 == 0 or f == total_frames - 1:
                print(f"   Rendered frame {f+1}/{total_frames} ({(f+1)/total_frames*100:.1f}%)")

        await browser.close()
    print("✅ All frames captured.")

def encode_video():
    print("🎞️ Encoding MP4 with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-r", str(FPS),
        "-i", "frames/frame_%04d.jpg",
        "-i", "audio.mp3",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd, check=True)
    print(f"🎉 {OUTPUT_VIDEO} rendered successfully! File size: {os.path.getsize(OUTPUT_VIDEO) / (1024*1024):.2f} MB")

async def main():
    start_time = time.time()
    await generate_audio()
    duration = get_audio_duration()
    print(f"⏱️ Audio duration: {duration:.2f} seconds")
    
    total_frames = int(duration * FPS) + 12 # slight pad
    await capture_frames(total_frames)
    encode_video()
    
    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"🏁 TOTAL RENDER TIME: {elapsed:.2f} seconds")
    print(f"==========================================")

if __name__ == "__main__":
    asyncio.run(main())
