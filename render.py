import os
import sys
import json
import base64
import math
import struct
import wave
import subprocess
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
        return 10.0

def generate_script(topic):
    import requests
    print(f"🧠 Generating cinematic 4-scene Hindi reel script for: '{topic}'...")
    
    prompt = f"""You are a master cinematic documentary director for @lostrealmshindi (exploring ancient Indian mysteries, sunken civilizations, and epic lore).
Create a captivating 4-scene Hindi video reel package for this topic: "{topic}".
Output ONLY valid JSON with this exact schema (no markdown, no quotes around json):
{{
  "title": "Hindi Title for YouTube Shorts with #Shorts",
  "scenes": [
    {{
      "id": 1,
      "badge": "रहस्यमयी द्वारका",
      "title": "समुद्र में डूबा स्वर्णिम शहर",
      "voiceover_hi": "हजारों साल पहले, अरब सागर की गहराइयों में एक पूरा शहर समा गया। वो शहर था — द्वारका। भगवान श्रीकृष्ण की स्वर्णिम नगरी!",
      "image_prompt": "Cinematic 9:16 vertical view of ancient stone temple gates submerged underwater in turquoise ocean with sun rays, 8k photorealistic"
    }},
    {{
      "id": 2,
      "badge": "पुरातत्व खोज",
      "title": "9000 साल पुरानी दीवारें",
      "voiceover_hi": "जब समुद्री पुरातत्वविदों ने गुजरात के तट पर खोज की, तो पानी के नीचे 9000 साल पुरानी विशाल दीवारें और खंभे मिले।",
      "image_prompt": "Scuba diver marine archaeologist exploring ancient submerged sandstone pillars underwater with flashlight, 9:16 cinematic photorealistic"
    }},
    {{
      "id": 3,
      "badge": "पौराणिक प्रमाण",
      "title": "महाभारत का जीवंत सच",
      "voiceover_hi": "महाभारत में वर्णित द्वारका कोई कल्पना नहीं, बल्कि एक ऐतिहासिक सच था—सोने और चांदी के महलों से सजी एक भव्य नगरी।",
      "image_prompt": "Glorious underwater view of a sprawling submerged ancient Indian golden city with temple spires on the seabed, 9:16 8k"
    }},
    {{
      "id": 4,
      "badge": "अनसुलझा रहस्य",
      "title": "क्या आज भी छिपे हैं दिव्य अस्त्र?",
      "voiceover_hi": "क्या इस समुद्र में आज भी श्रीकृष्ण के दिव्य अस्त्र और गुप्त खजाने दबे हैं? अपनी राय हमें कमेंट्स में बताएं!",
      "image_prompt": "Ancient sacred round bronze disk artifact with Sanskrit script half-buried in ocean sand underwater, 9:16 cinematic lighting"
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
                    {"role": "system", "content": "You are a professional YouTube Shorts director for @lostrealmshindi. Respond ONLY with valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=45
        )
        content = res.json()["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(content)
        print("✅ Custom script generated successfully via Antigravity Bridge")
        return data
    except Exception as e:
        print(f"⚠️ Script generation error ({e}), using default mythological template for '{topic}'")
        return {
            "title": f"{topic} #Shorts",
            "scenes": [
                {
                    "id": 1,
                    "badge": "प्राचीन रहस्य",
                    "title": topic,
                    "voiceover_hi": f"हजारों साल पहले, इतिहास के पन्नों में एक ऐसा रहस्य दर्ज हुआ जिसे आज तक कोई नहीं सुलझा सका—{topic}!",
                    "image_prompt": f"Mystical sacred ancient Indian cinematic temple scene about {topic}, glowing divine light, 9:16 photorealistic 8k"
                },
                {
                    "id": 2,
                    "badge": "पुरातत्व खोज",
                    "title": "रहस्यमयी साक्ष्य",
                    "voiceover_hi": "जब शोधकर्ताओं और पुरातत्वविदों ने गहराई से अध्ययन किया, तो उन्हें ऐसे साक्ष्य मिले जिन्होंने आधुनिक विज्ञान को भी हैरान कर दिया।",
                    "image_prompt": "Archaeologists investigating ancient mysterious Indian temple stone carvings and inscriptions, 9:16 cinematic lighting"
                },
                {
                    "id": 3,
                    "badge": "पौराणिक गाथा",
                    "title": "प्राचीन ग्रंथों का सच",
                    "voiceover_hi": "हमारे वेदों और पुराणों में वर्णित यह गाथा मात्र कोई कहानी नहीं, बल्कि उस काल के उन्नत ज्ञान का प्रत्यक्ष प्रमाण है।",
                    "image_prompt": "Dramatic cosmic visualization of ancient Indian Vedic architecture glowing with golden energy, 9:16 cinematic masterpiece"
                },
                {
                    "id": 4,
                    "badge": "अंतिम सवाल",
                    "title": "आपकी क्या राय है?",
                    "voiceover_hi": "क्या यह केवल संयोग था या किसी प्राचीन अलौकिक शक्ति का चमत्कार? अपनी राय हमें कमेंट्स में बताएं!",
                    "image_prompt": "Ancient sacred Indian artifact glowing mysteriously in dark stone chamber, 9:16 dramatic lighting"
                }
            ]
        }

def download_flow_image(scene_id, prompt):
    import requests
    print(f"🎨 Generating Google Flow image for Scene {scene_id}: '{prompt[:60]}...'")
    out_path = f"scene_{scene_id}.webp"
    try:
        res = requests.post(
            f"{BRIDGE_API_URL}/generate-image",
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt, "aspect_ratio": "9:16", "model": "flow"},
            timeout=120
        )
        if res.status_code == 200 and len(res.content) > 1000:
            with open(out_path, "wb") as f:
                f.write(res.content)
            print(f"✅ Scene {scene_id} image ready ({len(res.content)} bytes)")
            return out_path
    except Exception as e:
        print(f"⚠️ Flow image error on scene {scene_id}: {e}")
    return None

def generate_sarvam_audio(scene_id, text, api_key, speaker):
    import requests
    os.makedirs("audio", exist_ok=True)
    out_path = f"audio/audio_scene_{scene_id}.wav"
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
                "model": "bulbul:v3"
            },
            timeout=30
        )
        data = res.json()
        if "audios" in data and data["audios"]:
            audio_bytes = base64.b64decode(data["audios"][0])
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            print(f"✅ Scene {scene_id} voiceover generated via Sarvam AI")
            return out_path
    except Exception as e:
        print(f"⚠️ Sarvam AI error on scene {scene_id} ({e}), falling back to gTTS")
    
    from gtts import gTTS
    tts = gTTS(text=text, lang="hi", slow=False)
    mp3_path = f"audio/audio_scene_{scene_id}.mp3"
    tts.save(mp3_path)
    subprocess.run(["ffmpeg", "-y", "-i", mp3_path, out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

def build_composition(script_data, scene_images, scene_audios):
    scenes = script_data["scenes"]
    timeline = []
    current_time = 0.5
    
    concat_inputs = []
    filter_complex = ""
    
    for idx, sc in enumerate(scenes):
        audio_path = scene_audios[idx]
        dur = get_audio_duration(audio_path)
        start = current_time
        end = start + dur
        words = sc["voiceover_hi"].split()
        word_dur = dur / max(len(words), 1)
        
        words_timing = []
        for w_i, w in enumerate(words):
            words_timing.append({
                "word": w,
                "start": start + (w_i * word_dur),
                "end": start + ((w_i + 1) * word_dur)
            })
            
        timeline.append({
            "scene": sc,
            "image": scene_images[idx],
            "start": start,
            "end": end,
            "duration": dur,
            "words": words_timing
        })
        concat_inputs.extend(["-i", audio_path])
        filter_complex += f"[{idx}:a]apad=pad_dur=0.5[a{idx}];"
        current_time = end + 0.5
        
    total_duration = current_time + 1.0
    print(f"⏱️ Composition Timeline: {total_duration:.2f}s total across {len(timeline)} scenes")
    
    filter_complex += "".join([f"[a{i}]" for i in range(len(scenes))]) + f"concat=n={len(scenes)}:v=0:a=1[voconcat];"
    filter_complex += "[voconcat]adelay=500|500[vo_out]"
    subprocess.run(["ffmpeg", "-y"] + concat_inputs + ["-filter_complex", filter_complex, "-map", "[vo_out]", "audio/full_vo.wav"], check=True)
    
    print("🎶 Synthesizing Sacred Indian Classical Soundscape (Tanpura + Temple Bells + Pakhawaj)...")
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
            b_env = math.exp(-t_bell * 1.2)
            bell = (
                0.40 * math.sin(2 * math.pi * 587.33 * t_bell) * math.exp(-t_bell * 0.8) +
                0.30 * math.sin(2 * math.pi * 1185.0 * t_bell) * math.exp(-t_bell * 1.5)
            ) * b_env * 0.35
            samples[b_start + i] += bell

    for pt in scene_start_times:
        p_start = int(pt * sample_rate)
        p_len = int(0.7 * sample_rate)
        for i in range(p_len):
            if p_start + i >= num_samples: break
            t_p = i / sample_rate
            f_glide = 55.0 + 40.0 * (1.0 - t_p / 0.7)
            drum = math.sin(2 * math.pi * f_glide * t_p) * math.exp(-t_p * 6.0) * 0.35
            samples[p_start + i] += drum

    max_amp = max(max(abs(s) for s in samples), 0.001)
    norm = [s / max_amp * 0.75 for s in samples]
    with wave.open("audio/bgm.wav", "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(norm)}h", *[int(max(-32767, min(32767, s * 32767))) for s in norm]))

    print("🎚️ Master mixing full voiceover + acoustic soundbed at -14 LUFS...")
    cmd_mix = [
        "ffmpeg", "-y", "-i", "audio/full_vo.wav", "-i", "audio/bgm.wav",
        "-filter_complex", "[1:a]volume=0.22[bgm];[0:a][bgm]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=7:tp=-1.5[out]",
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", "audio/mix.mp3"
    ]
    subprocess.run(cmd_mix, check=True)
    print("✅ audio/mix.mp3 mastered successfully")

    scenes_html = ""
    for idx, sc_data in enumerate(timeline):
        sc = sc_data["scene"]
        img_src = sc_data["image"]
        words_spans = " ".join([
            f'<span class="k-word" id="kw_{idx}_{w_i}">{w["word"]}</span>'
            for w_i, w in enumerate(sc_data["words"])
        ])
        
        scenes_html += f"""
    <!-- Scene {idx + 1} -->
    <div class="scene-layer" id="scene_{idx}">
      <img class="scene-bg" id="bg_{idx}" src="{img_src}" alt="Scene {idx + 1}" data-layout-allow-overflow="true" />
      <div class="scene-vignette"></div>
      
      <!-- Scene Top Plaque -->
      <div class="top-plaque" id="plaque_{idx}" data-layout-allow-safe-zone="true">
        <div class="channel-pill">★ LOST REALMS HINDI</div>
        <div class="scene-badge">{sc["badge"]}</div>
        <div class="scene-title">{sc["title"]}</div>
      </div>

      <!-- Scene Subtitle Card -->
      <div class="sub-card-wrap" id="sub_wrap_{idx}" data-layout-allow-safe-zone="true">
        <div class="sub-card">
          <div class="sub-text-flow">
            {words_spans}
          </div>
        </div>
      </div>
    </div>
"""

    gsap_script = f"""
    gsap.registerPlugin();
    const tl = gsap.timeline({{ paused: true }});
    window.__timelines = {{ main: tl }};
"""

    for idx, sc_data in enumerate(timeline):
        s_start = sc_data["start"]
        s_end = sc_data["end"]
        s_dur = sc_data["duration"]
        
        gsap_script += f"""
    // SCENE {idx + 1}
    tl.to("#scene_{idx}", {{ opacity: 1, duration: 0.5 }}, {max(0, s_start - 0.3):.2f});
    tl.fromTo("#bg_{idx}", 
      {{ scale: 1.0, y: 0 }}, 
      {{ scale: 1.12, y: -25, duration: {s_dur + 0.8:.2f}, ease: "none" }}, 
      {max(0, s_start - 0.3):.2f}
    );
    tl.fromTo("#plaque_{idx}", 
      {{ opacity: 0, y: -30 }}, 
      {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, 
      {s_start:.2f}
    );
    tl.fromTo("#sub_wrap_{idx}", 
      {{ opacity: 0, y: 20 }}, 
      {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 
      {s_start:.2f}
    );
"""
        for w_i, w in enumerate(sc_data["words"]):
            w_start = w["start"]
            w_end = w["end"]
            gsap_script += f"""
    tl.to("#kw_{idx}_{w_i}", {{ color: "#ffdf00", textShadow: "0 0 16px rgba(255, 215, 0, 0.8)", scale: 1.08, duration: 0.1 }}, {w_start:.2f});
    tl.to("#kw_{idx}_{w_i}", {{ color: "#ffffff", textShadow: "none", scale: 1.0, duration: 0.1 }}, {w_end:.2f});
"""

        if idx < len(timeline) - 1:
            gsap_script += f"""
    tl.to("#scene_{idx}", {{ opacity: 0, duration: 0.5 }}, {s_end:.2f});
"""
        else:
            gsap_script += f"""
    tl.to("#scene_{idx}", {{ opacity: 1, duration: 1.0 }}, {total_duration - 1.0:.2f});
"""

    html = f"""<!doctype html>
<html lang="hi" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <title>Lost Realms Hindi - {script_data.get("title", "")}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Serif+Devanagari:wght@600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: #04090f;
      font-family: 'Noto Serif Devanagari', 'Cinzel', serif;
      -webkit-font-smoothing: antialiased;
    }}
    #stage {{
      position: relative;
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: #04090f;
    }}
    .scene-layer {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 1920px;
      opacity: 0;
      overflow: hidden;
    }}
    .scene-bg {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 1920px;
      object-fit: cover;
      transform-origin: center center;
    }}
    .scene-vignette {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 1920px;
      background: radial-gradient(circle at center, transparent 35%, rgba(0,0,0,0.55) 75%, rgba(0,0,0,0.9) 100%),
                  linear-gradient(180deg, rgba(0,0,0,0.75) 0%, transparent 20%, transparent 60%, rgba(0,0,0,0.9) 100%);
      pointer-events: none;
    }}
    .top-valence {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1080px;
      height: 110px;
      z-index: 50;
      pointer-events: none;
    }}
    .bottom-valence {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 1080px;
      height: 90px;
      z-index: 50;
      pointer-events: none;
      transform: rotate(180deg);
    }}
    .top-plaque {{
      position: absolute;
      top: 180px;
      left: 60px;
      right: 60px;
      display: flex;
      flex-direction: column;
      align-items: center;
      z-index: 40;
    }}
    .channel-pill {{
      background: linear-gradient(135deg, #1c150c, #2d2215);
      border: 2px solid #e0a93b;
      color: #ffd700;
      font-family: 'Cinzel', serif;
      font-size: 26px;
      font-weight: 800;
      letter-spacing: 3px;
      padding: 8px 30px;
      border-radius: 30px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.7), inset 0 0 10px rgba(224,169,59,0.3);
      margin-bottom: 12px;
    }}
    .scene-badge {{
      color: #ff9800;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      text-shadow: 0 2px 8px rgba(0,0,0,0.9);
      margin-bottom: 6px;
    }}
    .scene-title {{
      color: #ffffff;
      font-size: 40px;
      font-weight: 900;
      text-shadow: 0 3px 12px rgba(0,0,0,0.9), 0 0 25px rgba(212,175,55,0.4);
      text-align: center;
      line-height: 1.25;
    }}
    .sub-card-wrap {{
      position: absolute;
      bottom: 260px;
      left: 50px;
      right: 50px;
      z-index: 40;
    }}
    .sub-card {{
      background: rgba(10, 16, 24, 0.88);
      border: 2px solid #d4af37;
      border-radius: 20px;
      padding: 24px 30px;
      box-shadow: 0 15px 40px rgba(0,0,0,0.85), inset 0 0 20px rgba(212,175,55,0.2);
      backdrop-filter: blur(12px);
    }}
    .sub-text-flow {{
      color: #e0e0e0;
      font-size: 38px;
      font-weight: 700;
      line-height: 1.5;
      text-align: center;
    }}
    .k-word {{
      display: inline-block;
      margin: 0 5px;
      color: #ffffff;
    }}
  </style>
</head>
<body>
  <div id="stage" data-composition-id="main" data-width="1080" data-height="1920">
    <audio id="master_audio" src="audio/mix.mp3" preload="auto"></audio>
    <svg class="top-valence" viewBox="0 0 1080 110" preserveAspectRatio="none">
      <path d="M0,0 L1080,0 L1080,45 Q1020,80 960,45 Q900,80 840,45 Q780,80 720,45 Q660,80 600,45 Q540,80 480,45 Q420,80 360,45 Q300,80 240,45 Q180,80 120,45 Q60,80 0,45 Z" fill="#421010" stroke="#d4af37" stroke-width="3"/>
    </svg>
    <svg class="bottom-valence" viewBox="0 0 1080 110" preserveAspectRatio="none">
      <path d="M0,0 L1080,0 L1080,45 Q1020,80 960,45 Q900,80 840,45 Q780,80 720,45 Q660,80 600,45 Q540,80 480,45 Q420,80 360,45 Q300,80 240,45 Q180,80 120,45 Q60,80 0,45 Z" fill="#421010" stroke="#d4af37" stroke-width="3"/>
    </svg>

    {scenes_html}
  </div>

  <script>
{gsap_script}
  </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Sacred Cinema Multi-Scene index.html generated successfully!")

def main():
    print("🚀 Starting Sacred Cinema Cloud Video Render...")
    client_payload = {}
    if "CLIENT_PAYLOAD" in os.environ and os.environ["CLIENT_PAYLOAD"].strip():
        try:
            client_payload = json.loads(os.environ["CLIENT_PAYLOAD"])
        except Exception:
            pass

    topic = client_payload.get("topic") or "समुद्र की गहराइयों में छुपा द्वारका का रहस्य"
    sarvam_key = client_payload.get("sarvam_api_key") or SARVAM_DEFAULT_KEY
    sarvam_speaker = client_payload.get("sarvam_speaker") or SARVAM_DEFAULT_SPEAKER
    
    script_data = generate_script(topic)
    scenes = script_data["scenes"]

    print(f"🎨 Generating {len(scenes)} visual scene artworks in parallel via Google Flow...")
    scene_images = [None] * len(scenes)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_flow_image, sc["id"], sc["image_prompt"]): idx for idx, sc in enumerate(scenes)}
        for fut in futures:
            idx = futures[fut]
            scene_images[idx] = fut.result()

    print(f"🎙️ Generating voiceover for {len(scenes)} scenes via Sarvam AI (Mani)...")
    scene_audios = []
    for sc in scenes:
        audio_file = generate_sarvam_audio(sc["id"], sc["voiceover_hi"], sarvam_key, sarvam_speaker)
        scene_audios.append(audio_file)

    build_composition(script_data, scene_images, scene_audios)

    print("🎬 Rendering 1080x1920 24fps vertical video composition via HyperFrames...")
    cmd_render = ["npx", "-y", "hyperframes", "render", "-o", "render_action_test.mp4", "--fps", "24", "-q", "draft"]
    subprocess.run(cmd_render, check=True)

    print("📸 Extracting video thumbnail (thumb.jpg)...")
    cmd_thumb = ["ffmpeg", "-y", "-ss", "00:00:04", "-i", "render_action_test.mp4", "-vframes", "1", "-q:v", "2", "thumb.jpg"]
    subprocess.run(cmd_thumb, check=True)
    print("🎉 Complete Sacred Cinema Video Rendered & Saved!")

if __name__ == "__main__":
    main()
