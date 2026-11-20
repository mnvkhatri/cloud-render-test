import os
import sys
import time
import json
import asyncio
import subprocess
from playwright.async_api import async_playwright

WIDTH = 1080
HEIGHT = 1920
FPS = 24
OUTPUT_VIDEO = "render_action_test.mp4"

def get_payload():
    payload_str = os.environ.get("CLIENT_PAYLOAD", "{}")
    try:
        data = json.loads(payload_str) if payload_str else {}
        if isinstance(data, dict):
            return data
    except Exception as e:
        print(f"Warning: could not parse CLIENT_PAYLOAD: {e}")
    return {}

payload = get_payload()
topic = payload.get("topic") or "समुद्र की गहराइयों में छुपा द्वारका का रहस्य"
topic_id = payload.get("topic_id") or "TEST_001"
language = payload.get("language") or "hindi"

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    width: 1080px;
    height: 1920px;
    background: radial-gradient(circle at 50% 25%, #2a0845, #0a0118 70%);
    color: #fff;
    font-family: 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    position: relative;
  }}
  /* Ambient glow particles */
  .glow-orb {{
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(255, 140, 0, 0.25) 0%, rgba(255, 0, 128, 0) 70%);
    border-radius: 50%;
    filter: blur(50px);
    pointer-events: none;
  }}
  .orb-1 {{ top: 15%; left: 10%; }}
  .orb-2 {{ bottom: 15%; right: 10%; background: radial-gradient(circle, rgba(0, 255, 204, 0.2) 0%, rgba(0,0,0,0) 70%); }}

  /* Safe-Zone Card strictly within YouTube Shorts UI bounds */
  .card {{
    width: 920px;
    min-height: 1100px;
    background: rgba(20, 10, 35, 0.75);
    border: 3.5px solid rgba(255, 215, 0, 0.85);
    border-radius: 48px;
    box-shadow: 0 0 60px rgba(255, 215, 0, 0.35), inset 0 0 40px rgba(255, 215, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 70px 50px;
    text-align: center;
    backdrop-filter: blur(25px);
    z-index: 10;
  }}
  .badge {{
    background: linear-gradient(135deg, #ff8c00, #ff007f);
    padding: 16px 44px;
    border-radius: 50px;
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 50px;
    letter-spacing: 2px;
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(255, 0, 127, 0.4);
    text-transform: uppercase;
  }}
  h1 {{
    font-size: 68px;
    font-weight: 800;
    margin: 20px 0;
    color: #ffffff;
    line-height: 1.32;
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
    word-break: break-word;
  }}
  .highlight {{
    color: #ffd700;
    text-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
  }}
  .divider {{
    width: 240px;
    height: 6px;
    background: linear-gradient(90deg, transparent, #ffd700, transparent);
    margin: 40px 0;
    border-radius: 3px;
  }}
  .sub {{
    font-size: 40px;
    font-weight: 600;
    color: #e5e7eb;
    line-height: 1.45;
    margin-bottom: 45px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.6);
  }}
  .channel-pill {{
    display: flex;
    align-items: center;
    gap: 14px;
    background: rgba(255, 255, 255, 0.1);
    border: 1.5px solid rgba(255, 255, 255, 0.25);
    padding: 14px 36px;
    border-radius: 40px;
    font-size: 32px;
    font-weight: 700;
    color: #00ffcc;
    letter-spacing: 1px;
  }}
  .progress-bar-container {{
    width: 80%;
    height: 10px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 5px;
    margin-top: 40px;
    overflow: hidden;
  }}
  .progress-bar {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #00ffcc, #ff007f);
    border-radius: 5px;
  }}
</style>
</head>
<body>
  <div class="glow-orb orb-1"></div>
  <div class="glow-orb orb-2"></div>
  <div class="card">
    <div class="badge">⚔️ LOST REALMS HINDI</div>
    <h1>{topic}</h1>
    <div class="divider"></div>
    <div class="sub">प्राचीन भारत और खोई हुई सभ्यताओं का अनसुलझा रहस्य</div>
    <div class="channel-pill">
      <span>▶</span> @lostrealmshindi
    </div>
    <div class="progress-bar-container">
      <div class="progress-bar" id="pbar"></div>
    </div>
  </div>
  <script>
    function updateProgress(frameNum, totalFrames) {{
      const pct = (frameNum / totalFrames) * 100;
      document.getElementById('pbar').style.width = pct + '%';
      const card = document.querySelector('.card');
      const scale = 1 + 0.03 * Math.sin((frameNum / totalFrames) * Math.PI * 4);
      card.style.transform = 'scale(' + scale + ')';
    }}
  </script>
</body>
</html>
"""

def generate_audio():
    print(f"🎙️ Generating Hindi TTS for topic: '{topic}' using gTTS...")
    text = f"{topic}। इस रहस्यमयी प्राचीन कथा का सच आज भी दुनिया को हैरान कर देता है। जानिए खोई हुई सभ्यताओं के अनसुलझे रहस्य केवल Lost Realms पर।"
    from gtts import gTTS
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save("audio.mp3")
    print(f"✅ audio.mp3 generated ({os.path.getsize('audio.mp3')} bytes).")

def get_audio_duration():
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", "audio.mp3"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

async def capture_frames(total_frames):
    os.makedirs("frames", exist_ok=True)
    with open("index.html", "w", encoding="utf-8") as f:
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

def encode_video_and_thumb():
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
    print(f"🎉 {OUTPUT_VIDEO} rendered! Size: {os.path.getsize(OUTPUT_VIDEO) / (1024*1024):.2f} MB")

    print("🖼️ Generating high-res thumbnail thumb.jpg...")
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:01",
        "-i", OUTPUT_VIDEO,
        "-frames:v", "1",
        "-q:v", "2",
        "thumb.jpg"
    ]
    subprocess.run(thumb_cmd, check=True)
    print(f"✅ thumb.jpg generated ({os.path.getsize('thumb.jpg')} bytes).")

async def main():
    start_time = time.time()
    generate_audio()
    duration = get_audio_duration()
    print(f"⏱️ Audio duration: {duration:.2f} seconds")
    
    total_frames = int(duration * FPS) + 12
    await capture_frames(total_frames)
    encode_video_and_thumb()
    
    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"🏁 TOTAL RENDER TIME: {elapsed:.2f} seconds")
    print(f"==========================================")

if __name__ == "__main__":
    asyncio.run(main())
