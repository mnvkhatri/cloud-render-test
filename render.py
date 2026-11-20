import os
import sys
import time
import json
import wave
import struct
import math
import subprocess

OUTPUT_VIDEO = "render_action_test.mp4"
THUMBNAIL_IMG = "thumb.jpg"

def get_payload():
    payload_str = os.environ.get("CLIENT_PAYLOAD", "{}")
    try:
        data = json.loads(payload_str) if payload_str else {}
        if isinstance(data, dict):
            return data
    except Exception as e:
        print(f"Warning: could not parse CLIENT_PAYLOAD: {e}")
    return {}

def formulate_story(topic):
    clean_topic = topic.strip().replace("#Shorts", "").replace("#shorts", "").strip()
    
    # 3-act storytelling structure: Hook -> Sacred Legend -> Climax & Question
    shot1_text = f"क्या आप जानते हैं कि {clean_topic} के पीछे कौन सा गहरा रहस्य छुपा है?"
    shot2_text = "प्राचीन काल और महाकाव्यों में दर्ज यह गाथा आज भी वैज्ञानिकों और शोधकर्ताओं को सोचने पर विवश कर देती है।"
    shot3_text = "क्या यह केवल एक लोककथा है या हमारे प्राचीन इतिहास का साक्षात प्रमाण? अपनी राय कमेंट्स में बताएं।"
    
    full_vo = f"{shot1_text} {shot2_text} {shot3_text}"
    return clean_topic, shot1_text, shot2_text, shot3_text, full_vo

def generate_voiceover_and_bgm(clean_topic, full_vo):
    os.makedirs("audio", exist_ok=True)
    print(f"🎙️ Generating Hindi Voiceover for: '{clean_topic}'...")
    from gtts import gTTS
    tts = gTTS(text=full_vo, lang="hi", slow=False)
    tts.save("audio/vo.mp3")

    # Probe duration
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", "audio/vo.mp3"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    duration = float(res.stdout.strip())
    print(f"⏱️ Voiceover Duration: {duration:.2f} seconds")

    # Synthesize Indian Classical Acoustic BGM (Tanpura + Bells + Pakhawaj)
    print("🎶 Synthesizing Sacred Indian Classical Soundscape (Tanpura in D + Temple Bells + Pakhawaj)...")
    sample_rate = 44100
    total_dur = duration + 2.5
    num_samples = int(sample_rate * total_dur)
    samples = [0.0] * num_samples

    # Tanpura D Root Sa, Pa, High Sa, Low Sa
    tanpura_freqs = [220.0, 293.66, 293.66, 146.83]
    shot_times = [0.2, duration * 0.38, duration * 0.72, duration]

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
            0.2 * math.sin(2 * math.pi * f0 * 3 * t) +
            0.15 * math.sin(2 * math.pi * f0 * 4 * t)
        )
        drone = 0.25 * math.sin(2 * math.pi * 146.83 * t) + 0.20 * math.sin(2 * math.pi * 73.415 * t)
        samples[t_idx] += (tone * env * 0.35 + drone * 0.25)

    # Resonant Bronze Temple Bells
    for bt in shot_times:
        b_start = int(bt * sample_rate)
        b_len = int(3.5 * sample_rate)
        for i in range(b_len):
            if b_start + i >= num_samples: break
            t_bell = i / sample_rate
            b_env = math.exp(-t_bell * 1.2)
            bell = (
                0.40 * math.sin(2 * math.pi * 587.33 * t_bell) * math.exp(-t_bell * 0.8) +
                0.30 * math.sin(2 * math.pi * 1185.0 * t_bell) * math.exp(-t_bell * 1.5) +
                0.20 * math.sin(2 * math.pi * 1762.0 * t_bell) * math.exp(-t_bell * 2.2)
            ) * b_env * 0.35
            samples[b_start + i] += bell

    # Soft Earthen Pakhawaj Drum Impact
    for bt in shot_times:
        d_start = int(bt * sample_rate)
        d_len = int(1.0 * sample_rate)
        for i in range(d_len):
            if d_start + i >= num_samples: break
            t_drum = i / sample_rate
            d_env = math.exp(-t_drum * 4.0)
            f_glide = 55.0 + 40.0 * math.exp(-t_drum * 8.0)
            samples[d_start + i] += math.sin(2 * math.pi * f_glide * t_drum) * d_env * 0.4

    # Peak normalize
    max_amp = max(abs(s) for s in samples) or 1.0
    samples = [s * (0.65 / max_amp) for s in samples]

    # Write bgm.wav
    with wave.open('audio/bgm.wav', 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        data = bytearray()
        for s in samples:
            data.extend(struct.pack('<h', int(max(min(s, 1.0), -1.0) * 32767)))
        wav.writeframes(data)

    # Master mix at -14 LUFS
    print("🎚️ Master mixing Voiceover + BGM at -14 LUFS...")
    cmd_mix = [
        "ffmpeg", "-y", "-i", "audio/vo.mp3", "-i", "audio/bgm.wav",
        "-filter_complex", "[1:a]volume=0.22[bgm];[0:a][bgm]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=7:tp=-1.5[out]",
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", "audio/mix.mp3"
    ]
    subprocess.run(cmd_mix, check=True)
    print("✅ audio/mix.mp3 mastered successfully!")
    return duration, shot_times

def generate_sacred_cinema_html(clean_topic, shot1_text, shot2_text, shot3_text, duration, shot_times):
    t_shot1_end = shot_times[1]
    t_shot2_end = shot_times[2]
    
    html = f"""<!doctype html>
<html lang="hi" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <title>Lost Realms Hindi - {clean_topic}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Marcellus&family=Noto+Serif+Devanagari:wght@600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: #1a0f08;
      font-family: 'Noto Serif Devanagari', 'Cinzel', serif;
      -webkit-font-smoothing: antialiased;
    }}

    #stage {{
      position: relative;
      width: 1080px;
      height: 1920px;
      background: radial-gradient(circle at 50% 45%, #ecd8b9 0%, #d8ba93 50%, #b88f61 85%, #8c633a 100%);
      overflow: hidden;
    }}

    /* Aged parchment vignette overlay */
    .stage-vignette {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 50% 50%, transparent 55%, rgba(45, 20, 5, 0.45) 80%, rgba(20, 8, 2, 0.85) 100%);
      pointer-events: none;
      z-index: 5;
    }}

    /* Top and bottom ornate theater valence borders */
    .stage-border-top, .stage-border-bottom {{
      position: absolute;
      left: 0;
      width: 1080px;
      z-index: 90;
      pointer-events: none;
    }}
    .stage-border-top {{ top: 0; }}
    .stage-border-bottom {{ bottom: 0; transform: rotate(180deg); }}

    /* Channel Header */
    .channel-header {{
      position: absolute;
      top: 105px;
      left: 0;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 85;
    }}
    .channel-badge {{
      display: inline-flex;
      align-items: center;
      gap: 14px;
      padding: 12px 34px;
      background: rgba(43, 24, 13, 0.94);
      border: 2.5px solid #d4af37;
      border-radius: 40px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .channel-badge span {{
      font-family: 'Noto Serif Devanagari', 'Cinzel', serif;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: 4px;
      color: #ffd97d;
      text-transform: uppercase;
      text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }}

    /* Hanging Wooden Signboard Component */
    .signboard-wrapper {{
      position: absolute;
      top: -340px;
      left: 50%;
      margin-left: -440px;
      width: 880px;
      z-index: 75;
      transform-origin: 50% 0;
    }}
    .signboard-ropes {{
      width: 100%;
      height: 95px;
      display: flex;
      justify-content: space-around;
      padding: 0 120px;
    }}
    .rope {{
      width: 8px;
      height: 100%;
      background: repeating-linear-gradient(
        0deg,
        #795548,
        #795548 10px,
        #4e342e 10px,
        #4e342e 20px
      );
      box-shadow: 2px 2px 8px rgba(0,0,0,0.6);
    }}
    .signboard-plaque {{
      width: 880px;
      background: linear-gradient(180deg, #422817 0%, #29160a 100%);
      border: 6px solid #d4af37;
      border-radius: 20px;
      padding: 22px 36px;
      text-align: center;
      box-shadow: 0 18px 40px rgba(0,0,0,0.7), inset 0 0 20px rgba(212, 175, 55, 0.35);
      position: relative;
    }}
    .signboard-plaque::before {{
      content: "";
      position: absolute;
      top: 8px; left: 8px; right: 8px; bottom: 8px;
      border: 1.5px dashed #ffd97d;
      border-radius: 14px;
      pointer-events: none;
    }}
    .signboard-text {{
      font-family: 'Noto Serif Devanagari', 'Cinzel', serif;
      font-size: 44px;
      font-weight: 900;
      letter-spacing: 2px;
      color: #fff8e7;
      line-height: 1.28;
      text-shadow: 0 4px 12px rgba(0,0,0,0.9), 0 0 18px rgba(255, 217, 125, 0.5);
    }}
    .signboard-subtext {{
      font-family: 'Noto Serif Devanagari', 'Marcellus', serif;
      font-size: 26px;
      letter-spacing: 2px;
      color: #ffd97d;
      margin-top: 6px;
      text-shadow: 0 2px 6px rgba(0,0,0,0.8);
    }}

    /* Sacred Centerpiece Arena */
    .sacred-centerpiece {{
      position: absolute;
      top: 500px;
      left: 50%;
      margin-left: -400px;
      width: 800px;
      height: 800px;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 50;
      transform-origin: 50% 50%;
    }}
    .divine-aura {{
      position: absolute;
      width: 700px;
      height: 700px;
      background: radial-gradient(circle, rgba(255, 215, 0, 0.35) 0%, rgba(255, 109, 0, 0.2) 45%, rgba(0,0,0,0) 75%);
      border-radius: 50%;
      filter: blur(25px);
      pointer-events: none;
    }}

    /* Subtitle Card strictly in safe zone */
    .subtitle-wrapper {{
      position: absolute;
      bottom: 270px;
      left: 50%;
      margin-left: -480px;
      width: 960px;
      z-index: 85;
      text-align: center;
      pointer-events: none;
    }}
    .subtitle-card {{
      display: inline-block;
      max-width: 940px;
      padding: 22px 42px;
      background: rgba(26, 15, 8, 0.95);
      border: 3px solid #e0a93b;
      border-radius: 20px;
      box-shadow: 0 12px 35px rgba(0,0,0,0.7);
    }}
    .subtitle-text {{
      font-family: 'Noto Serif Devanagari', serif;
      font-size: 38px;
      font-weight: 700;
      line-height: 1.4;
      color: #ffffff;
      text-shadow: 0 2px 8px rgba(0,0,0,0.9);
    }}
    .subtitle-highlight {{
      color: #ffca28;
      font-weight: 900;
      text-shadow: 0 0 15px rgba(255, 202, 40, 0.5);
    }}

    /* Outro Bell */
    #outro-bell {{
      position: absolute;
      top: 480px;
      left: 50%;
      margin-left: -120px;
      width: 240px;
      height: 240px;
      z-index: 60;
      opacity: 0;
      transform-origin: 50% 0%;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{duration:.2f}" data-width="1080" data-height="1920">
    <audio id="a-roll-audio" src="audio/mix.mp3" data-start="0" data-duration="{duration:.2f}" data-track-index="2" data-volume="1"></audio>

    <div id="stage">
      <div class="stage-vignette" data-layout-ignore></div>

      <!-- Top Border SVG -->
      <svg class="stage-border-top" data-layout-ignore width="1080" height="95" viewBox="0 0 1080 95" fill="none">
        <path d="M0 0H1080V50C1040 75 1000 50 960 75C920 50 880 75 840 50C800 75 760 50 720 75C680 50 640 75 600 50C560 75 520 50 480 75C440 50 400 75 360 50C320 75 280 50 240 75C200 50 160 75 120 50C80 75 40 50 0 75V0Z" fill="#541212"/>
        <path d="M0 45C40 70 80 45 120 70C160 45 200 70 240 45C280 70 320 45 360 70C400 45 440 70 480 45C520 70 560 45 600 70C640 45 680 70 720 45C760 70 800 45 840 70C880 45 920 70 960 45C1000 70 1040 45 1080 70V76C1040 51 1000 76 960 51C920 76 880 51 840 76C800 51 760 76 720 51C680 76 640 51 600 76C560 51 520 76 480 51C440 76 400 51 360 76C320 51 280 76 240 51C200 76 160 51 120 76C80 51 40 76 0 51V45Z" fill="#e0a93b"/>
        <g fill="#fdfbf7">
          <circle cx="60" cy="50" r="4"/><circle cx="180" cy="50" r="4"/><circle cx="300" cy="50" r="4"/><circle cx="420" cy="50" r="4"/>
          <circle cx="540" cy="50" r="4"/><circle cx="660" cy="50" r="4"/><circle cx="780" cy="50" r="4"/><circle cx="900" cy="50" r="4"/>
          <circle cx="1020" cy="50" r="4"/>
        </g>
      </svg>

      <!-- Bottom Border SVG -->
      <svg class="stage-border-bottom" data-layout-ignore width="1080" height="95" viewBox="0 0 1080 95" fill="none">
        <path d="M0 0H1080V50C1040 75 1000 50 960 75C920 50 880 75 840 50C800 75 760 50 720 75C680 50 640 75 600 50C560 75 520 50 480 75C440 50 400 75 360 50C320 75 280 50 240 75C200 50 160 75 120 50C80 75 40 50 0 75V0Z" fill="#541212"/>
        <path d="M0 45C40 70 80 45 120 70C160 45 200 70 240 45C280 70 320 45 360 70C400 45 440 70 480 45C520 70 560 45 600 70C640 45 680 70 720 45C760 70 800 45 840 70C880 45 920 70 960 45C1000 70 1040 45 1080 70V76C1040 51 1000 76 960 51C920 76 880 51 840 76C800 51 760 76 720 51C680 76 640 51 600 76C560 51 520 76 480 51C440 76 400 51 360 76C320 51 280 76 240 51C200 76 160 51 120 76C80 51 40 76 0 51V45Z" fill="#e0a93b"/>
        <g fill="#fdfbf7">
          <circle cx="60" cy="50" r="4"/><circle cx="180" cy="50" r="4"/><circle cx="300" cy="50" r="4"/><circle cx="420" cy="50" r="4"/>
          <circle cx="540" cy="50" r="4"/><circle cx="660" cy="50" r="4"/><circle cx="780" cy="50" r="4"/><circle cx="900" cy="50" r="4"/>
          <circle cx="1020" cy="50" r="4"/>
        </g>
      </svg>

      <!-- Channel Brand / Badge -->
      <div class="channel-header" data-layout-ignore>
        <div class="channel-badge">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="#ffd97d"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <span>LOST REALMS HINDI</span>
        </div>
      </div>

      <!-- Hanging Wooden Signboard Component -->
      <div id="signboard" class="signboard-wrapper" data-layout-allow-safe-zone data-layout-allow-overlap>
        <div class="signboard-ropes" data-layout-ignore>
          <div class="rope"></div>
          <div class="rope"></div>
        </div>
        <div class="signboard-plaque" data-layout-allow-overlap>
          <div id="signboard-title" class="signboard-text" data-layout-allow-safe-zone>{clean_topic}</div>
          <div id="signboard-desc" class="signboard-subtext" data-layout-allow-safe-zone data-layout-ignore>खोई हुई सभ्यताओं का रहस्य</div>
        </div>
      </div>

      <!-- Sacred Centerpiece: Celestial Sudarshana Chakra & Trishul Mandapam -->
      <div id="centerpiece" class="sacred-centerpiece" data-layout-allow-overlap>
        <div class="divine-aura"></div>
        <!-- Intricate Sacred Vector Art -->
        <svg id="sacred-mandala" width="700" height="700" viewBox="0 0 700 700" fill="none">
          <defs>
            <radialGradient id="goldRadial" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#fff8e7"/>
              <stop offset="40%" stop-color="#ffd700"/>
              <stop offset="85%" stop-color="#ff8c00"/>
              <stop offset="100%" stop-color="#b85d00"/>
            </radialGradient>
            <filter id="divineGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="14" result="blur"/>
              <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
          </defs>
          <!-- Outer Celestial Ray Ring -->
          <g id="chakra-rays" stroke="url(#goldRadial)" stroke-width="4" opacity="0.85">
            <line x1="350" y1="50" x2="350" y2="120"/>
            <line x1="350" y1="580" x2="350" y2="650"/>
            <line x1="50" y1="350" x2="120" y2="350"/>
            <line x1="580" y1="350" x2="650" y2="350"/>
            <line x1="138" y1="138" x2="188" y2="188"/>
            <line x1="512" y1="512" x2="562" y2="562"/>
            <line x1="138" y1="562" x2="188" y2="512"/>
            <line x1="512" y1="188" x2="562" y2="138"/>
          </g>
          <!-- Ornate Filigree Rings -->
          <circle cx="350" cy="350" r="260" stroke="#ffd700" stroke-width="5" stroke-dasharray="14 8" fill="none"/>
          <circle cx="350" cy="350" r="220" stroke="#d4af37" stroke-width="3" fill="rgba(43, 24, 13, 0.45)"/>
          <circle cx="350" cy="350" r="170" stroke="#ffd700" stroke-width="4" fill="none"/>
          <!-- Inner Sacred Trishul & Sun Emblem -->
          <g filter="url(#divineGlow)">
            <path d="M350 170 L350 510" stroke="url(#goldRadial)" stroke-width="12" stroke-linecap="round"/>
            <path d="M300 240 Q350 310 400 240" stroke="url(#goldRadial)" stroke-width="10" fill="none" stroke-linecap="round"/>
            <path d="M300 240 L285 200 L305 210 Z" fill="#ffd700"/>
            <path d="M400 240 L415 200 L395 210 Z" fill="#ffd700"/>
            <path d="M350 170 L338 130 L350 110 L362 130 Z" fill="#fff8e7"/>
            <path d="M320 330 L380 330 L320 370 L380 370 Z" fill="#ff8c00" stroke="#ffd700" stroke-width="3"/>
          </g>
          <!-- Lotus Petals Circle -->
          <g fill="none" stroke="#ffd700" stroke-width="2.5" opacity="0.9">
            <path d="M350 90 Q370 130 350 170 Q330 130 350 90 Z"/>
            <path d="M350 610 Q370 570 350 530 Q330 570 350 610 Z"/>
            <path d="M90 350 Q130 370 170 350 Q130 330 90 350 Z"/>
            <path d="M610 350 Q570 370 530 350 Q570 330 610 350 Z"/>
          </g>
        </svg>
      </div>

      <!-- Outro Temple Bell -->
      <div id="outro-bell" data-layout-allow-overlap>
        <svg width="240" height="240" viewBox="0 0 240 240" fill="none">
          <circle cx="120" cy="20" r="14" fill="none" stroke="#d4af37" stroke-width="6"/>
          <path d="M80 60 C80 40 160 40 160 60 L180 150 C190 180 50 180 60 150 Z" fill="url(#goldRadial)" stroke="#4e342e" stroke-width="5"/>
          <circle cx="120" cy="180" r="18" fill="#ffd700" stroke="#4e342e" stroke-width="4"/>
        </svg>
      </div>

      <!-- Subtitles Card strictly in safe zone -->
      <div class="subtitle-wrapper" data-layout-allow-safe-zone data-layout-allow-overlap>
        <div class="subtitle-card" data-layout-allow-overlap>
          <div id="subtitle-text" class="subtitle-text" data-layout-allow-safe-zone>
            {shot1_text}
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ defaults: {{ ease: "power2.inOut" }} }});

    // Initial setup
    gsap.set("#signboard", {{ y: 0, rotation: 0 }});
    gsap.set("#centerpiece", {{ scale: 0.85, opacity: 0 }});
    gsap.set("#outro-bell", {{ opacity: 0, scale: 0 }});

    // Ambient continuous motion
    gsap.to("#chakra-rays", {{
      rotation: 360,
      transformOrigin: "350px 350px",
      duration: 35,
      repeat: 4,
      ease: "none"
    }});

    gsap.to(".divine-aura", {{
      scale: 1.15,
      opacity: 0.7,
      duration: 3,
      repeat: 8,
      yoyo: true,
      ease: "sine.inOut"
    }});

    // -------------------------------------------------------------
    // SHOT 1: 0.0s - {t_shot1_end:.2f}s | THE HOOK
    // -------------------------------------------------------------
    tl.to("#signboard", {{
      y: 450,
      duration: 1.2,
      ease: "elastic.out(1, 0.45)"
    }}, 0.2);

    tl.to("#signboard", {{
      rotation: 2.5,
      duration: 1.8,
      repeat: 3,
      yoyo: true,
      ease: "sine.inOut"
    }}, 1.4);

    tl.to("#centerpiece", {{
      opacity: 1,
      scale: 1.0,
      duration: 1.5,
      ease: "power2.out"
    }}, 0.6);

    // -------------------------------------------------------------
    // SHOT 2: {t_shot1_end:.2f}s - {t_shot2_end:.2f}s | THE SACRED HISTORY
    // -------------------------------------------------------------
    tl.call(() => {{
      document.getElementById("signboard-title").innerText = "प्राचीन गाथा व रहस्य";
      document.getElementById("signboard-desc").innerText = "महाकाव्यों में छुपा सत्य";
      document.getElementById("subtitle-text").innerHTML = '{shot2_text}';
    }}, null, {t_shot1_end:.2f});

    tl.to("#centerpiece", {{
      scale: 1.12,
      duration: 2.0,
      ease: "power2.inOut"
    }}, {t_shot1_end + 0.3:.2f});

    // -------------------------------------------------------------
    // SHOT 3: {t_shot2_end:.2f}s - {duration:.2f}s | CLIMAX & OUTRO CTA
    // -------------------------------------------------------------
    tl.call(() => {{
      document.getElementById("signboard-title").innerText = "आपकी क्या राय है?";
      document.getElementById("signboard-desc").innerText = "कमेंट्स में ज़रूर बताएं ✨";
      document.getElementById("subtitle-text").innerHTML = '{shot3_text}';
    }}, null, {t_shot2_end:.2f});

    tl.to("#centerpiece", {{
      opacity: 0.35,
      scale: 0.8,
      duration: 1.0
    }}, {t_shot2_end:.2f});

    tl.to("#outro-bell", {{
      opacity: 1,
      scale: 1.2,
      duration: 0.8,
      ease: "back.out(1.7)"
    }}, {t_shot2_end + 0.2:.2f});

    tl.to("#outro-bell", {{
      rotation: 18,
      transformOrigin: "50% 0%",
      duration: 0.45,
      repeat: 8,
      yoyo: true,
      ease: "sine.inOut"
    }}, {t_shot2_end + 0.8:.2f});

    // Register with HyperFrames
    window.__timelines = window.__timelines || {{}};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Sacred Cinema index.html generated!")

def render_with_hyperframes():
    print("🎬 Rendering composition via HyperFrames...")
    cmd = ["npx", "-y", "hyperframes", "render", "-o", OUTPUT_VIDEO, "--fps", "24", "-q", "draft"]
    subprocess.run(cmd, check=True)
    print(f"🎉 Video rendered successfully! File size: {os.path.getsize(OUTPUT_VIDEO) / (1024*1024):.2f} MB")

def extract_thumbnail():
    print("🖼️ Extracting high-contrast cinematic thumbnail...")
    cmd = [
        "ffmpeg", "-y", "-ss", "00:00:03", "-i", OUTPUT_VIDEO,
        "-frames:v", "1", "-q:v", "2", THUMBNAIL_IMG
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ {THUMBNAIL_IMG} extracted ({os.path.getsize(THUMBNAIL_IMG)} bytes).")

def main():
    start_time = time.time()
    payload = get_payload()
    raw_topic = payload.get("topic") or "समुद्र की गहराइयों में छुपा द्वारका का रहस्य"
    
    clean_topic, shot1_text, shot2_text, shot3_text, full_vo = formulate_story(raw_topic)
    duration, shot_times = generate_voiceover_and_bgm(clean_topic, full_vo)
    generate_sacred_cinema_html(clean_topic, shot1_text, shot2_text, shot3_text, duration, shot_times)
    render_with_hyperframes()
    extract_thumbnail()
    
    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"🏁 TOTAL SACRED CINEMA RENDER TIME: {elapsed:.2f} seconds")
    print(f"==========================================")

if __name__ == "__main__":
    main()
