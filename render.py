import os
import sys
import json
import base64
import math
import struct
import wave
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

SARVAM_DEFAULT_KEY = "sk_y4laizws_uJw1vMXtUnIwgZ35791walZ7"
SARVAM_DEFAULT_SPEAKER = "mani"
BRIDGE_API_URL = "https://bridge.mnvcloud.online"

def get_audio_duration(path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
        return float(subprocess.check_output(cmd).decode().strip())
    except Exception:
        res = subprocess.run(["ffmpeg", "-i", path], stderr=subprocess.PIPE, text=True)
        for line in res.stderr.splitlines():
            if "Duration:" in line:
                time_str = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = time_str.split(":")
                return float(h)*3600 + float(m)*60 + float(s)
        return 5.0

def generate_script(topic):
    import requests
    print(f"🧠 Generating cinematic 8-scene screenplay for: '{topic}'...")
    
    prompt = f"""You are a master animation director and viral storyteller for @lostrealmshindi creating a 52-second YouTube Short / Instagram Reel.
Topic: "{topic}".
Art Style: Vibrant 2D Indian cartoon animation style (clean sharp linework, rich cel shading, modern Amar Chitra Katha & Disney animated film aesthetic, 16:9 widescreen).

CRITICAL SCRIPT CONSTRAINTS:
1. Total spoken duration MUST be 50-55 seconds.
2. In Hindi, 50 seconds equals EXACTLY 100 to 115 words TOTAL across the entire script.
3. Divide into EXACTLY 8 sequential scenes (approx 12-14 Hindi words per scene).
4. Each scene MUST have:
   - "id": scene number (1 to 8)
   - "voiceover_hi": EXACTLY 1 concise, punchy, dramatic Hindi sentence (10-14 words max). NEVER write long paragraphs!
   - "image_prompt": A unique, distinct 16:9 visual description featuring the specific action/character of this exact moment in 2D Indian cartoon animation style. Every single scene must have a completely different visual composition and action!
5. The story arc must be complete:
   - Scene 1: Attention-grabbing question or shocking mystery.
   - Scene 2-3: Historical and mythological background.
   - Scene 4-6: The incredible event, miracle, or scientific phenomenon.
   - Scene 7: Modern scientific confirmation or enduring wonder.
   - Scene 8: Strong philosophical conclusion and call to comment!

Return ONLY valid JSON with this exact schema (no markdown, no quotes around json):
{{
  "youtube_title": "Shorts Title in Hindi with #Shorts",
  "header_line_1": "Top Hook Line 1 (White)",
  "header_line_2": "Top Hook Line 2 (Yellow)",
  "scenes": [
    {{
      "id": 1,
      "voiceover_hi": "One punchy sentence in Hindi (12 words).",
      "image_prompt": "Unique visual description for scene 1"
    }}
  ]
}}"""

    try:
        res = requests.post(
            f"{BRIDGE_API_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "antigravity",
                "messages": [
                    {"role": "system", "content": "You are a professional animation director for @lostrealmshindi. Respond ONLY with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=45
        )
        content = res.json()["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(content)
        total_words = sum(len(s.get("voiceover_hi", "").split()) for s in data.get("scenes", []))
        print(f"✅ Generated script with {len(data.get('scenes', []))} scenes ({total_words} total words)")
        return data
    except Exception as e:
        print(f"⚠️ Script generation error ({e}), using default fallback for '{topic}'")
        return {
            "youtube_title": f"{topic} #Shorts",
            "header_line_1": "महाभारत का सबसे",
            "header_line_2": "शक्तिशाली रहस्य",
            "scenes": [
                {
                    "id": 1,
                    "voiceover_hi": "महाभारत युद्ध में क्या अर्जुन या कर्ण ही सबसे शक्तिशाली योद्धा थे?",
                    "image_prompt": "Vibrant 2D Indian cartoon animation of epic Kurukshetra battlefield at sunset with ancient golden war chariots and fluttering flags"
                },
                {
                    "id": 2,
                    "voiceover_hi": "प्राचीन ग्रंथों के अनुसार, वहाँ एक ऐसा योद्धा आया जिसके पास केवल तीन दिव्य बाण थे।",
                    "image_prompt": "Close-up 2D cartoon animation of a glowing golden quiver holding three divine shining arrows"
                },
                {
                    "id": 3,
                    "voiceover_hi": "यह थे महाबली बर्बरीक, जिन्होंने माँ कामाख्या की तपस्या से अमोघ वरदान पाया था।",
                    "image_prompt": "Young heroic warrior Barbareek in gleaming golden armor holding a celestial bow in vibrant 2D cartoon style"
                },
                {
                    "id": 4,
                    "voiceover_hi": "उनकी शक्ति परखने स्वयं भगवान श्रीकृष्ण पीपल के विशाल वृक्ष के नीचे आए।",
                    "image_prompt": "Lord Krishna with peacock crown standing serenely under a giant sacred Peepal tree in 2D cartoon animation"
                },
                {
                    "id": 5,
                    "voiceover_hi": "कान्हा ने कहा: अपने एक ही तीर से इस पेड़ के हर पत्ते को छेद कर दिखाओ।",
                    "image_prompt": "Lord Krishna challenging Barbareek by pointing up toward the dense green tree canopy in 2D cartoon style"
                },
                {
                    "id": 6,
                    "voiceover_hi": "बर्बरीक का पहला बाण चलते ही हर पत्ता छिद गया, और बाण कान्हा के पैर पर मंडराने लगा!",
                    "image_prompt": "A glowing divine arrow hovering inches above Lord Krishna's lotus foot where a single leaf is hidden"
                },
                {
                    "id": 7,
                    "voiceover_hi": "संसार की रक्षा के लिए श्रीकृष्ण ने बर्बरीक से उनका शीश दान में माँग लिया।",
                    "image_prompt": "Smiling crowned head of Barbareek on a golden ceremonial platter receiving divine blessings in 2D cartoon style"
                },
                {
                    "id": 8,
                    "voiceover_hi": "कलयुग में भगवान ने उन्हें खाटू श्याम का अमर स्वरूप दिया। कमेंट में लिखें—जय श्री श्याम!",
                    "image_prompt": "Grand temple sanctum of Khatu Shyam Ji with glowing oil lamps and devotees with folded hands in 2D cartoon style"
                }
            ]
        }

def download_flow_image(scene_id, prompt):
    import requests
    print(f"🎨 Generating 16:9 Google Flow image for Scene {scene_id} via bridge.mnvcloud.online...")
    out_path = f"scene_{scene_id:02d}.webp"
    
    full_prompt = f"Vibrant 2D Indian cartoon animation style, modern Amar Chitra Katha and Disney animated feature film aesthetic, clean sharp linework, rich cel shading, saturated colors, 16:9 widescreen: {prompt}"
    
    for attempt in range(1, 4):
        try:
            # Unique dynamic seed prevents bridge backend caching or race collisions
            seed = int(time.time() * 1000) % 999999 + scene_id * 1013
            res = requests.post(
                f"{BRIDGE_API_URL}/generate-image",
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                json={
                    "prompt": full_prompt,
                    "aspect_ratio": "16:9",
                    "model": "flow",
                    "seed": seed
                },
                timeout=90
            )
            if res.status_code == 200 and len(res.content) > 5000:
                with open(out_path, "wb") as f:
                    f.write(res.content)
                print(f"✅ Scene {scene_id} Flow image ready ({len(res.content)} bytes, seed: {seed})")
                return out_path
        except Exception as e:
            print(f"⚠️ Flow image attempt {attempt} failed for Scene {scene_id} ({e})")
            time.sleep(3)
            
    print(f"❌ Failed to download Flow image for Scene {scene_id}")
    return None

def generate_sarvam_audio(scene_id, text, api_key, speaker):
    import requests
    os.makedirs("audio", exist_ok=True)
    out_path = f"audio/audio_scene_{scene_id:02d}.wav"
    print(f"🎙️ Generating Sarvam AI voiceover (speaker: {speaker}) for Scene {scene_id}...")
    try:
        res = requests.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={
                "api-subscription-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "inputs": [text],
                "target_language_code": "hi-IN",
                "speaker": speaker,
                "model": "bulbul:v3",
                "pace": 1.15
            },
            timeout=30
        )
        data = res.json()
        if "audios" in data and data["audios"]:
            audio_bytes = base64.b64decode(data["audios"][0])
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            print(f"✅ Scene {scene_id} Sarvam audio ready")
            return out_path
    except Exception as e:
        print(f"⚠️ Sarvam AI error on Scene {scene_id} ({e}), using gTTS fallback")

    from gtts import gTTS
    tts = gTTS(text=text, lang="hi", slow=False)
    mp3_path = f"audio/audio_scene_{scene_id:02d}.mp3"
    tts.save(mp3_path)
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

def build_composition(script_data, scene_images, scene_audios):
    scenes = script_data["scenes"]
    header_1 = script_data.get("header_line_1", "महाभारत का सबसे")
    header_2 = script_data.get("header_line_2", "शक्तिशाली योद्धा")
    
    timeline = []
    current_time = 0.4
    concat_inputs = []
    filter_complex = ""
    global_word_counter = 0

    for idx, sc in enumerate(scenes):
        audio_path = scene_audios[idx]
        dur = get_audio_duration(audio_path)
        start = current_time
        end = start + dur
        
        words = sc["voiceover_hi"].split()
        chunk_size = 6
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        chunk_dur = dur / max(len(chunks), 1)
        
        scene_chunks = []
        c_time = start
        for c_idx, chunk in enumerate(chunks):
            c_start = c_time
            c_end = c_time + chunk_dur
            c_time = c_end
            
            w_dur = chunk_dur / max(len(chunk), 1)
            chunk_words = []
            for w_idx, w in enumerate(chunk):
                w_start = c_start + (w_idx * w_dur)
                w_end = w_start + w_dur
                global_word_counter += 1
                chunk_words.append({
                    "id": f"w_{global_word_counter}",
                    "text": w,
                    "start": round(w_start, 2),
                    "end": round(w_end, 2)
                })
            scene_chunks.append({
                "chunk_id": f"c_{idx}_{c_idx}",
                "start": round(c_start, 2),
                "end": round(c_end, 2),
                "words": chunk_words
            })
            
        timeline.append({
            "scene": sc,
            "id": idx + 1,
            "image": scene_images[idx] or f"assets_cartoon/scene_{(idx % 12) + 1:02d}.jpg",
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(dur, 2),
            "chunks": scene_chunks
        })
        concat_inputs.extend(["-i", audio_path])
        filter_complex += f"[{idx}:a]apad=pad_dur=0.25[a{idx}];"
        current_time = end + 0.25

    total_duration = min(round(current_time + 0.3, 2), 58.0)
    print(f"⏱️ Composition Timeline: {total_duration}s across {len(timeline)} scenes with {global_word_counter} synchronized words")

    filter_complex += "".join([f"[a{i}]" for i in range(len(scenes))]) + f"concat=n={len(scenes)}:v=0:a=1[voconcat];"
    filter_complex += "[voconcat]adelay=400|400[vo_out]"
    subprocess.run(["ffmpeg", "-y"] + concat_inputs + ["-filter_complex", filter_complex, "-map", "[vo_out]", "audio/full_vo.wav"], check=True)

    # Acoustic Soundscape Synthesis (Tanpura + Bronze Temple Bells + Pakhawaj Drum Glides)
    sample_rate = 44100
    num_samples = int(sample_rate * total_duration)
    samples = [0.0] * num_samples
    tanpura_freqs = [220.0, 293.66, 293.66, 146.83]

    for t_idx in range(num_samples):
        t = t_idx / sample_rate
        cycle_pos = t % 8.0
        str_idx = int(cycle_pos // 2.0)
        pluck_t = cycle_pos % 2.0
        env = (pluck_t / 0.05) if pluck_t < 0.05 else math.exp(-(pluck_t - 0.05) * 1.2)
        f0 = tanpura_freqs[str_idx]
        tone = (
            0.5 * math.sin(2 * math.pi * f0 * t) +
            0.3 * math.sin(2 * math.pi * f0 * 2 * t) +
            0.2 * math.sin(2 * math.pi * f0 * 3 * t)
        )
        drone = 0.25 * math.sin(2 * math.pi * 146.83 * t) + 0.20 * math.sin(2 * math.pi * 73.415 * t)
        samples[t_idx] += (tone * env * 0.35 + drone * 0.25)

    scene_start_times = [sc["start"] for sc in timeline]
    for bt in scene_start_times:
        b_start = int(bt * sample_rate)
        b_len = int(3.5 * sample_rate)
        for i in range(b_len):
            if b_start + i >= num_samples: break
            t_bell = i / sample_rate
            bell = (
                0.40 * math.sin(2 * math.pi * 587.33 * t_bell) * math.exp(-t_bell * 0.8) +
                0.30 * math.sin(2 * math.pi * 1185.0 * t_bell) * math.exp(-t_bell * 1.5)
            ) * math.exp(-t_bell * 1.2) * 0.35
            samples[b_start + i] += bell

        p_len = int(0.7 * sample_rate)
        for i in range(p_len):
            if b_start + i >= num_samples: break
            t_p = i / sample_rate
            f_glide = 55.0 + 40.0 * (1.0 - t_p / 0.7)
            drum = math.sin(2 * math.pi * f_glide * t_p) * math.exp(-t_p * 6.0) * 0.35
            samples[b_start + i] += drum

    max_amp = max(max(abs(s) for s in samples), 0.001)
    norm = [s / max_amp * 0.75 for s in samples]
    with wave.open("audio/bgm.wav", "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(norm)}h", *[int(max(-32767, min(32767, s * 32767))) for s in norm]))

    cmd_mix = [
        "ffmpeg", "-y", "-i", "audio/full_vo.wav", "-i", "audio/bgm.wav",
        "-filter_complex", "[1:a]volume=0.20[bgm];[0:a][bgm]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=7:tp=-1.5[out]",
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", "audio/mix.mp3"
    ]
    subprocess.run(cmd_mix, check=True)
    print("✅ audio/mix.mp3 mastered at -14 LUFS")

    # Images HTML
    images_html = ""
    for idx, sc in enumerate(timeline):
        images_html += f'    <img class="scene-frame" id="scene-{sc["id"]}" src="{sc["image"]}" alt="Scene {sc["id"]}" style="z-index: {idx+1}">\n'

    # Captions HTML
    captions_html = ""
    for sc in timeline:
        for chunk in sc["chunks"]:
            captions_html += f'    <div class="caption-chunk" id="{chunk["chunk_id"]}">\n'
            for w in chunk["words"]:
                captions_html += f'      <span class="caption-word" id="{w["id"]}">{w["text"]}</span>\n'
            captions_html += '    </div>\n'

    # GSAP Timelines
    gsap_script = f"""
    const tl = gsap.timeline({{ paused: true }});
    window.__timelines = {{ main: tl }};
    const timelineData = {json.dumps(timeline, ensure_ascii=False)};

    timelineData.forEach((sc, index) => {{
      const imgEl = `#scene-${{sc.id}}`;
      tl.to(imgEl, {{ autoAlpha: 1, duration: 0.35, ease: "power1.out" }}, sc.start);
      
      const scaleTo = 1.05 + (index % 3) * 0.02;
      const xTo = (index % 2 === 0 ? 1 : -1) * 15;
      tl.fromTo(imgEl, 
        {{ scale: 1.0, x: 0 }}, 
        {{ scale: scaleTo, x: xTo, duration: sc.duration + 0.3, ease: "none" }}, 
        sc.start
      );

      if (index < timelineData.length - 1) {{
        const nextStart = timelineData[index + 1].start;
        tl.to(imgEl, {{ autoAlpha: 0, duration: 0.3, ease: "power1.in" }}, nextStart);
      }}

      sc.chunks.forEach((chunk) => {{
        const cId = `#${{chunk.chunk_id}}`;
        tl.to(cId, {{ autoAlpha: 1, duration: 0.15, ease: "power1.out" }}, chunk.start);
        tl.to(cId, {{ autoAlpha: 0, duration: 0.15, ease: "power1.in" }}, chunk.end - 0.08);

        chunk.words.forEach((w) => {{
          const wId = `#${{w.id}}`;
          tl.to(wId, {{ className: "caption-word active", duration: 0.08 }}, w.start);
          tl.to(wId, {{ className: "caption-word", duration: 0.08 }}, w.end);
        }});
      }});
    }});
"""

    html = f"""<!doctype html>
<html lang="hi">
<head>
  <meta charset="utf-8">
  <title>Lost Realms Hindi - {script_data.get("youtube_title", "")}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Noto+Sans+Devanagari:wght@600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body, html {{
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: #090503;
      font-family: 'Noto Sans Devanagari', sans-serif;
      -webkit-font-smoothing: antialiased;
    }}
    #stage {{
      position: relative;
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 50%, #1a0d08 0%, #0d0604 60%, #050201 100%);
    }}
    .ambient-glow {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 1920px;
      pointer-events: none;
      z-index: 2;
      background: radial-gradient(circle at 50% 42%, rgba(255, 170, 0, 0.08) 0%, transparent 65%);
    }}
    .top-header {{
      position: absolute;
      top: 130px;
      left: 0;
      width: 1080px;
      text-align: center;
      z-index: 10;
    }}
    .channel-tag {{
      display: inline-block;
      font-family: 'Cinzel', serif;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: 5px;
      color: #ffd700;
      background: rgba(35, 12, 6, 0.85);
      border: 1.5px solid rgba(212, 175, 55, 0.6);
      border-radius: 20px;
      padding: 6px 28px;
      margin-bottom: 22px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.8);
      text-transform: uppercase;
    }}
    .main-title {{
      font-family: 'Noto Sans Devanagari', sans-serif;
      font-size: 68px;
      font-weight: 900;
      line-height: 1.22;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .title-white {{
      color: #ffffff;
      text-shadow: 0 5px 25px rgba(0, 0, 0, 0.95), 0 2px 4px rgba(0,0,0,0.8);
    }}
    .title-yellow {{
      color: #ffd700;
      text-shadow: 0 0 30px rgba(255, 215, 0, 0.6), 0 5px 25px rgba(0, 0, 0, 0.95);
    }}
    .viewport-16-9 {{
      position: absolute;
      top: 490px;
      left: 0;
      width: 1080px;
      height: 608px;
      overflow: hidden;
      z-index: 5;
      background: #000000;
      border-top: 3.5px solid #d4af37;
      border-bottom: 3.5px solid #d4af37;
      box-shadow: 0 15px 50px rgba(0, 0, 0, 0.95);
    }}
    .scene-frame {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 608px;
      object-fit: cover;
      opacity: 0;
      visibility: hidden;
      transform-origin: center center;
    }}
    .captions-wrapper {{
      position: absolute;
      bottom: 250px;
      left: 50%;
      transform: translateX(-50%);
      width: 940px;
      min-height: 160px;
      z-index: 10;
      display: flex;
      justify-content: center;
      align-items: center;
      text-align: center;
    }}
    .caption-chunk {{
      position: absolute;
      width: 100%;
      opacity: 0;
      visibility: hidden;
      font-family: 'Noto Sans Devanagari', sans-serif;
      font-size: 44px;
      line-height: 1.4;
      font-weight: 800;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      gap: 12px 16px;
      padding: 16px 28px;
      background: rgba(14, 5, 2, 0.88);
      border: 2px solid rgba(212, 175, 55, 0.5);
      border-radius: 24px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.9);
      backdrop-filter: blur(8px);
    }}
    .caption-word {{
      display: inline-block;
      color: #ffffff;
      font-family: 'Noto Sans Devanagari', sans-serif;
      font-weight: 800;
      transition: color 0.15s ease, transform 0.15s ease;
      text-shadow: 0 2px 6px rgba(0,0,0,0.9);
    }}
    .caption-word.active {{
      color: #ffd700;
      font-weight: 900;
      transform: scale(1.14);
      text-shadow: 0 0 22px rgba(255, 215, 0, 0.85), 0 2px 6px rgba(0,0,0,0.9);
    }}
  </style>
</head>
<body>
  <div id="stage" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{total_duration}">
    <div class="ambient-glow"></div>
    <div class="top-header" data-layout-allow-safe-zone>
      <div class="channel-tag">&#9733; LOST REALMS HINDI &#9733;</div>
      <h1 class="main-title">
        <span class="title-white">{header_1}</span><br>
        <span class="title-yellow">{header_2}</span>
      </h1>
    </div>
    <div class="viewport-16-9" data-layout-allow-overflow>
{images_html}
    </div>
    <div class="captions-wrapper" data-layout-allow-overlap>
{captions_html}
    </div>
    <audio id="master_audio" src="audio/mix.mp3" data-start="0" data-duration="{total_duration}" preload="auto"></audio>
  </div>
  <script>
{gsap_script}
  </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Modern 2D Cartoon Reel index.html generated successfully!")

def main():
    print("🚀 Starting @lostrealmshindi Cloud Video Render Pipeline...")
    client_payload = {}
    if "CLIENT_PAYLOAD" in os.environ and os.environ["CLIENT_PAYLOAD"].strip():
        try:
            client_payload = json.loads(os.environ["CLIENT_PAYLOAD"])
        except Exception:
            pass

    topic = client_payload.get("topic") or "महाभारत का सबसे शक्तिशाली योद्धा: महाबली बर्बरीक"
    sarvam_key = client_payload.get("sarvam_api_key") or SARVAM_DEFAULT_KEY
    sarvam_speaker = client_payload.get("sarvam_speaker") or SARVAM_DEFAULT_SPEAKER
    
    script_data = generate_script(topic)
    scenes = script_data["scenes"]

    print(f"🎨 Generating {len(scenes)} visual 16:9 cartoon scene artworks sequentially via Google Flow...")
    scene_images = [None] * len(scenes)
    for idx, sc in enumerate(scenes):
        img_file = download_flow_image(sc["id"], sc["image_prompt"])
        scene_images[idx] = img_file
        time.sleep(2)

    print(f"🎙️ Generating voiceover for {len(scenes)} scenes via Sarvam AI ({sarvam_speaker})...")
    scene_audios = []
    for sc in scenes:
        audio_file = generate_sarvam_audio(sc["id"], sc["voiceover_hi"], sarvam_key, sarvam_speaker)
        scene_audios.append(audio_file)

    build_composition(script_data, scene_images, scene_audios)

    print("🎬 Rendering 1080x1920 30fps vertical video composition via HyperFrames...")
    cmd_render = ["npx", "-y", "hyperframes", "render", "-o", "render_action_test.mp4", "--fps", "30", "-q", "standard"]
    subprocess.run(cmd_render, check=True)

    print("📸 Extracting video thumbnail (thumb.jpg)...")
    cmd_thumb = ["ffmpeg", "-y", "-ss", "00:00:04", "-i", "render_action_test.mp4", "-vframes", "1", "-q:v", "2", "thumb.jpg"]
    subprocess.run(cmd_thumb, check=True)
    print("🎉 Complete @lostrealmshindi Reel Rendered & Saved!")

if __name__ == "__main__":
    main()
