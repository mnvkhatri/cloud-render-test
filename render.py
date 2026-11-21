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

def generate_script(topic, video_type="short"):
    import requests
    is_long = (video_type == "long_video")
    print(f"🧠 Generating screenplay for '{topic}' (format: {'16:9 Long Video' if is_long else '9:16 Short'})...")
    
    if is_long:
        prompt = f"""You are a master viral animation director and financial educator for @FinHackHindi creating a full-length 16:9 widescreen YouTube video breakdown.
Topic: "{topic}".
Visual Style: Modern 2D vector cartoon financial illustration style, clean vibrant graphic novel aesthetic, sharp bold linework, rich saturated colors, 16:9 widescreen.

CRITICAL SCRIPT CONSTRAINTS:
1. Divide into EXACTLY 10 sequential scenes (approx 16-22 Hindi words per scene).
2. Total duration will be around 1.5 to 2.5 minutes of high-density financial education.
3. Each scene MUST have:
   - "id": scene number (1 to 10)
   - "voiceover_hi": EXACTLY 1 clear, punchy, authoritative Hindi sentence (16-22 words max). Explain the strategy, math, or psychological secret in crisp conversational Hindi.
   - "image_prompt": A unique, distinct 16:9 visual description featuring the specific financial scenario/characters/action of this moment in modern 2D cartoon financial graphic style (e.g., contrasting two people, compounding graph, portfolio asset allocation pie, salary budgeting envelopes, real estate vs mutual funds, digital app screen).
4. The story arc must follow:
   - Scene 1: The bold hook & counter-intuitive truth.
   - Scene 2-3: The hidden trap or why 95% of people remain middle-class.
   - Scene 4-5: The math / framework breakdown (e.g. 50-30-20, Rule of 72, index fund compounding, emergency fund rule).
   - Scene 6-7: Step-by-step actionable plan with concrete numbers.
   - Scene 8-9: Real-world compounding milestones (Age 20 vs 25 vs 30).
   - Scene 10: Powerful summary, call to subscribe to @FinHackHindi and take action today.
5. Provide high-CTR thumbnail elements:
   - "youtube_title": Catchy YouTube Title in Hindi & English (e.g. "... | Fin Hack Hindi")
   - "header_line_1": Punchy Main Title Line 1 (White text on thumbnail, max 4-6 words)
   - "header_line_2": Highlighted Title Line 2 (Yellow text on thumbnail, max 3-5 words)
   - "stat_badge": High-impact thumbnail metric badge (e.g. "₹0 से ₹1 करोड़ रोडमैप", "100% प्रैक्टिकल फॉर्मूला")

Return ONLY valid JSON with this exact schema (no markdown, no quotes around json):
{{
  "youtube_title": "Full YouTube Video Title",
  "header_line_1": "Top Hook Line 1",
  "header_line_2": "Highlight Line 2",
  "stat_badge": "Key Metric Badge",
  "scenes": [
    {{
      "id": 1,
      "voiceover_hi": "One punchy sentence in Hindi (18 words).",
      "image_prompt": "Unique visual description for scene 1"
    }}
  ]
}}"""
    else:
        prompt = f"""You are a master viral animation director and financial educator for @FinHackHindi creating a 52-second YouTube Short / Instagram Reel.
Topic: "{topic}".
Visual Style: Modern 2D vector cartoon financial illustration style, clean vibrant graphic novel aesthetic, sharp bold linework, rich saturated colors, 16:9 widescreen.

CRITICAL SCRIPT CONSTRAINTS:
1. Total spoken duration MUST be 50-55 seconds.
2. In Hindi, 50 seconds equals EXACTLY 100 to 115 words TOTAL across the entire script.
3. Divide into EXACTLY 8 sequential scenes (approx 12-14 Hindi words per scene).
4. Each scene MUST have:
   - "id": scene number (1 to 8)
   - "voiceover_hi": EXACTLY 1 concise, punchy, dramatic Hindi sentence (10-14 words max). Explain money, math, rules, or secrets in simple Hindi terms anyone can understand.
   - "image_prompt": A unique, distinct 16:9 visual description featuring the specific financial scenario/characters/action of this moment in modern 2D cartoon financial graphic style (e.g., contrasting two people, piggy bank compounding, stock chart, credit card trap, bank vault, currency notes).
5. The story arc must follow the viral financial framework:
   - Scene 1: Hard-hitting hook question or shocking money reality.
   - Scene 2-3: The common mistake or problem that keeps 95% of people broke.
   - Scene 4-6: The mathematical secret, hack, or exact rule.
   - Scene 7: Real-world result (e.g. compounding milestone or money saved).
   - Scene 8: Punchy actionable advice and call to action ("सब्सक्राइब करें Fin Hack Hindi").
6. Provide thumbnail elements:
   - "youtube_title": Shorts Title in Hindi with #Shorts #FinHackHindi
   - "header_line_1": Top Hook Line 1 (White)
   - "header_line_2": Top Hook Line 2 (Yellow)
   - "stat_badge": Key Metric Badge (e.g. "₹15,000 से ₹1 करोड़")

Return ONLY valid JSON with this exact schema (no markdown, no quotes around json):
{{
  "youtube_title": "Shorts Title in Hindi with #Shorts #FinHackHindi",
  "header_line_1": "Top Hook Line 1",
  "header_line_2": "Highlight Line 2",
  "stat_badge": "Key Metric Badge",
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
                    {"role": "system", "content": "You are a professional financial animation director for @FinHackHindi. Respond ONLY with valid JSON."},
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
            "youtube_title": f"{topic} | Fin Hack Hindi",
            "header_line_1": "अमीर बनने का",
            "header_line_2": "मास्टरप्लान",
            "stat_badge": "₹0 से ₹1 करोड़ रोडमैप",
            "scenes": [
                {
                    "id": 1,
                    "voiceover_hi": "क्या केवल सही वित्तीय योजना और अनुशासन से कोई भी आम इंसान 30 की उम्र तक करोड़पति बन सकता है?",
                    "image_prompt": "Modern 2D cartoon illustration of a salaried young Indian man looking thoughtfully at his smartphone showing growing investments"
                },
                {
                    "id": 2,
                    "voiceover_hi": "ज़्यादातर लोग अपनी 20s में सारी सैलरी महंगे गैजेट्स और लाइफस्टाइल पर खर्च कर देते हैं।",
                    "image_prompt": "2D cartoon animation of ordinary people spending banknotes on shopping bags while savings drain away"
                },
                {
                    "id": 3,
                    "voiceover_hi": "लेकिन अमीर लोग सबसे पहले अपने पैसे को काम पर लगाते हैं ताकि पैसा उनके लिए कमा सके।",
                    "image_prompt": "Vibrant 2D graphic of smart investor relaxing while digital money gears and golden coins compound automatically"
                },
                {
                    "id": 4,
                    "voiceover_hi": "पहला नियम: 50-30-20 का बजट फॉर्मूला अपनाएं, जहां 20 प्रतिशत पैसा हर महीने निवेश में जाना अनिवार्य है।",
                    "image_prompt": "2D vector cartoon of an automated smartphone budgeting app dividing salary into three colorful glowing buckets"
                },
                {
                    "id": 5,
                    "voiceover_hi": "दूसरा नियम: कम से कम 6 महीने के खर्चों का इमरजेंसी फंड लिक्विड फंड या फिक्स्ड डिपॉजिट में तैयार रखें।",
                    "image_prompt": "2D cartoon of a glowing safety shield protecting family savings vault from financial rain and storms"
                },
                {
                    "id": 6,
                    "voiceover_hi": "तीसरा नियम: निफ्टी 50 या बड़े इंडेक्स फंड्स में बिना रुके हर महीने अनुशासित SIP शुरू करें।",
                    "image_prompt": "2D cartoon financial stock chart curving steeply upwards with bull horns and percentage symbols"
                },
                {
                    "id": 7,
                    "voiceover_hi": "चौथा नियम: कभी भी हाई-इंटरेस्ट क्रेडिट कार्ड डेट या पर्सनल लोन के जाल में न फंसें।",
                    "image_prompt": "2D cartoon of cutting up high interest credit cards with scissors liberating golden coins"
                },
                {
                    "id": 8,
                    "voiceover_hi": "कंपाउंडिंग का जादू समय के साथ काम करता है—जितनी जल्दी शुरुआत, उतना विशाल वेल्थ क्रिएशन!",
                    "image_prompt": "2D cartoon calendar pages flipping rapidly with a golden money tree growing into massive wealth"
                },
                {
                    "id": 9,
                    "voiceover_hi": "10 सालों में यही छोटा सा अनुशासन आपके बैंक बैलेंस को करोड़ों के मुकाम पर पहुंचा देगा।",
                    "image_prompt": "2D cartoon of an open golden bank vault overflowing with glowing Indian currency bundles and a 1 Crore milestone sign"
                },
                {
                    "id": 10,
                    "voiceover_hi": "स्मार्ट मनी हैक्स और वेल्थ क्रिएशन के लिए अभी सब्सक्राइब करें Fin Hack Hindi, और अपनी वेल्थ जर्नी आज ही शुरू करें!",
                    "image_prompt": "Hero character smiling confidently pointing at a golden subscribe bell button in 2D cartoon style"
                }
            ]
        }

def clean_watermark(raw_path, out_path):
    try:
        cmd_probe = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", raw_path]
        dim = subprocess.check_output(cmd_probe).decode().strip().split("x")
        w, h = int(dim[0]), int(dim[1])
        box_w = max(int(w * 0.14), 100)
        box_h = max(int(h * 0.18), 90)
        x_pos = max(0, w - box_w - int(w * 0.01))
        y_pos = max(0, h - box_h - int(h * 0.01))
        cmd_delogo = [
            "ffmpeg", "-y", "-i", raw_path,
            "-vf", f"delogo=x={x_pos}:y={y_pos}:w={box_w}:h={box_h}",
            "-q:v", "2",
            out_path
        ]
        subprocess.run(cmd_delogo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path
    except Exception as e:
        subprocess.run(["ffmpeg", "-y", "-i", raw_path, "-q:v", "2", out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path

def download_flow_image(scene_id, prompt):
    import requests
    print(f"🎨 Generating 16:9 Google Flow image for Scene {scene_id} via bridge.mnvcloud.online...")
    raw_path = f"raw_scene_{scene_id:02d}.webp"
    out_path = f"scene_{scene_id:02d}.jpg"
    
    full_prompt = f"Modern 2D vector cartoon financial illustration style, clean vibrant graphic novel aesthetic, sharp bold linework, rich saturated colors, business wealth and money theme, 16:9 widescreen: {prompt}"
    
    for attempt in range(1, 4):
        try:
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
                with open(raw_path, "wb") as f:
                    f.write(res.content)
                clean_watermark(raw_path, out_path)
                print(f"✅ Scene {scene_id} ready with Gemini watermark cleanly removed (seed: {seed})")
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

def build_composition(script_data, scene_images, scene_audios, video_type="short"):
    is_long = (video_type == "long_video")
    scenes = script_data["scenes"]
    header_1 = script_data.get("header_line_1", "अमीर बनने का")
    header_2 = script_data.get("header_line_2", "मास्टरप्लान")
    stat_badge = script_data.get("stat_badge", "₹0 से ₹1 करोड़ रोडमैप")
    
    width = 1920 if is_long else 1080
    height = 1080 if is_long else 1920
    
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
        chunk_size = 7 if is_long else 6
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

    total_duration = round(current_time + 0.5, 2)
    print(f"⏱️ Composition Timeline: {total_duration}s across {len(timeline)} scenes with {global_word_counter} synchronized words (Mode: {'16:9 Long Video' if is_long else '9:16 Short'})")

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
    window.__timelines = {{ main: tl, thumbnail: gsap.timeline({{ paused: true }}) }};
    const timelineData = {json.dumps(timeline, ensure_ascii=False)};

    timelineData.forEach((sc, index) => {{
      const imgEl = `#scene-${{sc.id}}`;
      tl.to(imgEl, {{ autoAlpha: 1, duration: 0.35, ease: "power1.out" }}, sc.start);
      
      const scaleTo = 1.08 + (index % 3) * 0.02;
      const xTo = (index % 2 === 0 ? 1 : -1) * 20;
      tl.fromTo(imgEl, 
        {{ scale: 1.03, x: 0 }}, 
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

    thumb_bg = scene_images[0] or f"assets_cartoon/scene_01.jpg"
    thumb_w = 1920 if is_long else 1080
    thumb_h = 1080 if is_long else 1920

    if is_long:
        # 16:9 Widescreen Layout Styles
        layout_styles = f"""
    body, html {{
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #080402;
      font-family: 'Noto Sans Devanagari', sans-serif;
      -webkit-font-smoothing: antialiased;
    }}
    #stage {{
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #050201;
    }}
    .ambient-glow {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1920px;
      height: 1080px;
      pointer-events: none;
      z-index: 2;
      background: radial-gradient(circle at 50% 50%, transparent 50%, rgba(0,0,0,0.7) 100%);
    }}
    .watermark-badge {{
      position: absolute;
      top: 36px;
      left: 48px;
      z-index: 10;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-family: 'Cinzel', serif;
      font-size: 24px;
      font-weight: 900;
      letter-spacing: 4px;
      color: #ffd700;
      background: rgba(14, 5, 2, 0.85);
      border: 1.5px solid rgba(212, 175, 55, 0.6);
      border-radius: 14px;
      padding: 8px 24px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.85);
      text-transform: uppercase;
    }}
    .viewport-main {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      z-index: 1;
      background: #000000;
    }}
    .scene-frame {{
      position: absolute;
      top: 0;
      left: 0;
      width: 1920px;
      height: 1080px;
      object-fit: cover;
      opacity: 0;
      visibility: hidden;
      transform-origin: center center;
    }}
    .captions-wrapper {{
      position: absolute;
      bottom: 50px;
      left: 50%;
      transform: translateX(-50%);
      width: 1500px;
      min-height: 120px;
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
      font-size: 48px;
      line-height: 1.35;
      font-weight: 800;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      align-items: center;
      gap: 14px 20px;
      padding: 16px 36px;
      background: rgba(10, 4, 2, 0.88);
      border: 2px solid rgba(212, 175, 55, 0.5);
      border-radius: 22px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.95);
      backdrop-filter: blur(10px);
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
      text-shadow: 0 0 24px rgba(255, 215, 0, 0.85), 0 2px 6px rgba(0,0,0,0.9);
    }}
"""
        stage_content = f"""
  <div id="stage" data-composition-id="main" data-width="1920" data-height="1080" data-duration="{total_duration}">
    <div class="ambient-glow"></div>
    <div class="watermark-badge">&#9733; FIN HACK HINDI &#9733;</div>
    <div class="viewport-main" data-layout-allow-overflow>
{images_html}
    </div>
    <div class="captions-wrapper" data-layout-allow-overlap>
{captions_html}
    </div>
    <audio id="master_audio" src="audio/mix.mp3" data-start="0" data-duration="{total_duration}" preload="auto"></audio>
  </div>
"""
    else:
        # 9:16 Vertical Short Layout Styles
        layout_styles = f"""
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
"""
        stage_content = f"""
  <div id="stage" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{total_duration}">
    <div class="ambient-glow"></div>
    <div class="top-header" data-layout-allow-safe-zone>
      <div class="channel-tag">&#9733; FIN HACK HINDI &#9733;</div>
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
"""

    # Dedicated High-CTR Thumbnail Composition
    if is_long:
        thumb_composition = f"""
  <div id="thumb-stage" data-composition-id="thumbnail" data-width="1920" data-height="1080" data-duration="1" style="position:relative; width:1920px; height:1080px; overflow:hidden; background:#000;">
    <img src="{thumb_bg}" style="position:absolute; top:0; left:0; width:1920px; height:1080px; object-fit:cover; filter:brightness(0.70) contrast(1.18);">
    <div style="position:absolute; inset:0; background:linear-gradient(90deg, rgba(8,4,2,0.95) 0%, rgba(8,4,2,0.82) 48%, rgba(8,4,2,0.2) 100%);"></div>
    <div style="position:absolute; top:120px; left:120px; max-width:1150px; z-index:10;">
      <div style="display:inline-block; font-family:'Cinzel', serif; font-size:32px; font-weight:900; color:#ffd700; background:rgba(20,8,4,0.92); border:2px solid #ffd700; border-radius:14px; padding:10px 28px; letter-spacing:4px; margin-bottom:28px; text-transform:uppercase; box-shadow:0 6px 25px rgba(0,0,0,0.8);">&#9733; FIN HACK HINDI &#9733;</div>
      <div style="font-family:'Noto Sans Devanagari', sans-serif; font-size:84px; font-weight:900; color:#ffffff; line-height:1.18; text-shadow:0 6px 30px rgba(0,0,0,1); margin-bottom:14px;">{header_1}</div>
      <div style="font-family:'Noto Sans Devanagari', sans-serif; font-size:94px; font-weight:900; color:#ffd700; line-height:1.18; text-shadow:0 0 35px rgba(255,215,0,0.65), 0 6px 30px rgba(0,0,0,1);">{header_2}</div>
      <div style="margin-top:36px; display:inline-block; font-family:'Noto Sans Devanagari', sans-serif; font-size:42px; font-weight:900; color:#00e676; background:rgba(0,35,15,0.92); border:2.5px solid #00e676; border-radius:16px; padding:12px 32px; box-shadow:0 8px 30px rgba(0,230,118,0.4); text-shadow:0 2px 10px rgba(0,0,0,0.8);">&#9650; {stat_badge}</div>
    </div>
  </div>
"""
    else:
        thumb_composition = f"""
  <div id="thumb-stage" data-composition-id="thumbnail" data-width="1080" data-height="1920" data-duration="1" style="position:relative; width:1080px; height:1920px; overflow:hidden; background:#090503;">
    <img src="{thumb_bg}" style="position:absolute; top:490px; left:0; width:1080px; height:608px; object-fit:cover;">
    <div style="position:absolute; top:130px; left:0; width:1080px; text-align:center; z-index:10;">
      <div style="display:inline-block; font-family:'Cinzel', serif; font-size:28px; font-weight:800; letter-spacing:5px; color:#ffd700; background:rgba(35,12,6,0.85); border:1.5px solid rgba(212,175,55,0.6); border-radius:20px; padding:6px 28px; margin-bottom:22px;">&#9733; FIN HACK HINDI &#9733;</div>
      <h1 style="font-family:'Noto Sans Devanagari', sans-serif; font-size:68px; font-weight:900; line-height:1.22; text-transform:uppercase;">
        <span style="color:#ffffff; text-shadow:0 5px 25px rgba(0,0,0,0.95);">{header_1}</span><br>
        <span style="color:#ffd700; text-shadow:0 0 30px rgba(255,215,0,0.6), 0 5px 25px rgba(0,0,0,0.95);">{header_2}</span>
      </h1>
    </div>
  </div>
"""

    html = f"""<!doctype html>
<html lang="hi">
<head>
  <meta charset="utf-8">
  <title>Fin Hack Hindi - {script_data.get("youtube_title", "")}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@800;900&family=Noto+Sans+Devanagari:wght@600;700;800;900&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
{layout_styles}
  </style>
</head>
<body>
{stage_content}
{thumb_composition}
  <script>
{gsap_script}
  </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Composition index.html generated successfully! ({'16:9 1920x1080' if is_long else '9:16 1080x1920'})")

def main():
    print("🚀 Starting @FinHackHindi Cloud Video Render Pipeline...")
    client_payload = {}
    if "CLIENT_PAYLOAD" in os.environ and os.environ["CLIENT_PAYLOAD"].strip():
        try:
            client_payload = json.loads(os.environ["CLIENT_PAYLOAD"])
        except Exception:
            pass

    # Extract parameters from client_payload or sys.argv
    topic = client_payload.get("topic") or (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else "20 से 30 की उम्र में अमीर बनने का मास्टरप्लान")
    sarvam_key = client_payload.get("sarvam_api_key") or SARVAM_DEFAULT_KEY
    sarvam_speaker = client_payload.get("sarvam_speaker") or SARVAM_DEFAULT_SPEAKER
    video_type = (client_payload.get("video_type") or (sys.argv[3] if len(sys.argv) > 3 else "short")).lower().strip()
    is_long = (video_type == "long_video")
    
    print(f"📌 Mode: {'16:9 Widescreen Long Video (1920x1080)' if is_long else '9:16 Vertical Short (1080x1920)'}")
    print(f"📌 Topic: {topic}")
    
    script_data = generate_script(topic, video_type)
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

    build_composition(script_data, scene_images, scene_audios, video_type)

    print(f"🎬 Rendering {'1920x1080' if is_long else '1080x1920'} 30fps video composition via HyperFrames...")
    cmd_render = ["npx", "-y", "hyperframes", "render", "-o", "render_action_test.mp4", "--fps", "30", "-q", "standard"]
    subprocess.run(cmd_render, check=True)

    print(f"📸 Generating high-CTR YouTube thumbnail (thumb.jpg) in {'16:9 (1920x1080)' if is_long else '9:16 (1080x1920)'}...")
    thumb_generated = False
    try:
        snap_dir = os.path.abspath("thumb_snaps")
        os.makedirs(snap_dir, exist_ok=True)
        cmd_snap = ["npx", "-y", "hyperframes", "snapshot", ".", "--composition", "thumbnail", "--frames", "1", "-o", snap_dir]
        res_snap = subprocess.run(cmd_snap, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_snap.returncode == 0:
            snaps = [f for f in os.listdir(snap_dir) if f.endswith(".png") and not f.startswith("contact")]
            if snaps:
                snap_file = os.path.join(snap_dir, sorted(snaps)[0])
                subprocess.run(["ffmpeg", "-y", "-i", snap_file, "-q:v", "2", "thumb.jpg"], check=True)
                thumb_generated = True
                print(f"✅ Generated high-CTR custom thumbnail thumb.jpg ({'1920x1080' if is_long else '1080x1920'})")
    except Exception as e:
        print(f"⚠️ Thumbnail snapshot error: {e}")

    if not thumb_generated or not os.path.exists("thumb.jpg"):
        print("⚠️ Snapshot fallback: extracting frame from rendered MP4...")
        subprocess.run(["ffmpeg", "-y", "-ss", "00:00:04", "-i", "render_action_test.mp4", "-vframes", "1", "-q:v", "2", "thumb.jpg"], check=True)

    print("🎉 Complete @FinHackHindi Video Rendered & Saved!")

if __name__ == "__main__":
    main()
