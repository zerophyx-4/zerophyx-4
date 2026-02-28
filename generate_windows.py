import requests
import base64
import os
import json
import re

# Load config
with open("window-config.json", "r") as f:
    config = json.load(f)

FONT_NAME  = config.get("font", "inter")
BANNER     = config.get("banner", "")
BLUR       = config.get("blur", 4)
SHADOW     = config.get("shadow", True)
WIDTH      = config.get("width", 600)

def fetch_google_font(font_name):
    try:
        api_name = "+".join(w.capitalize() for w in font_name.split())
        url = f"https://fonts.googleapis.com/css2?family={api_name}&display=swap"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None, font_name
        font_urls = re.findall(r'url\((https://fonts\.gstatic\.com[^)]+)\)', r.text)
        if not font_urls:
            return None, font_name
        fr = requests.get(font_urls[0])
        if fr.status_code != 200:
            return None, font_name
        b64 = base64.b64encode(fr.content).decode("utf-8")
        face = f"@font-face{{font-family:'{font_name}';src:url('data:font/woff2;base64,{b64}') format('woff2');}}"
        return face, font_name
    except:
        return None, font_name

def get_file_base64(path):
    if not path or not os.path.exists(path):
        return None, None
    ext = path.split(".")[-1].lower()
    mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","gif":"image/gif"}.get(ext,"image/png")
    with open(path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode("utf-8")

def generate_window(title, content_lines, filename):
    font_face, font_family = fetch_google_font(FONT_NAME)
    font_css = font_face if font_face else ""

    line_height  = 24
    padding      = 24
    title_bar_h  = 38
    content_h    = len(content_lines) * line_height + padding * 2
    height       = title_bar_h + content_h

    # Shadow filter
    shadow_filter = ""
    shadow_attr   = ""
    if SHADOW:
        shadow_filter = '<filter id="shadow" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.6"/></filter>'
        shadow_attr   = 'filter="url(#shadow)"'

    # Banner background
    bg_svg = ""
    if BANNER:
        mime, b64 = get_file_base64(BANNER)
        if b64:
            blur_filter = f'<filter id="bg-blur"><feGaussianBlur stdDeviation="{BLUR}"/></filter>' if BLUR > 0 else ""
            blur_attr   = 'filter="url(#bg-blur)"' if BLUR > 0 else ""
            bg_svg = f'{blur_filter}<image href="data:{mime};base64,{b64}" x="0" y="{title_bar_h}" width="{WIDTH}" height="{content_h}" preserveAspectRatio="xMidYMid slice" opacity="0.3" {blur_attr}/>'

    # Content lines
    lines_svg = ""
    for i, line in enumerate(content_lines):
        y = title_bar_h + padding + (i * line_height) + 14
        if "—" in line:
            parts = line.split("—", 1)
            key = parts[0].strip()
            val = parts[1].strip() if len(parts) > 1 else ""
            lines_svg += f'<text x="{padding}" y="{y}" font-family="{font_family}, sans-serif" font-size="13.5" fill="#cccccc"><tspan font-weight="600" fill="#ffffff">{key}</tspan><tspan fill="#555"> — </tspan><tspan>{val}</tspan></text>\n'
        elif line.startswith("◦"):
            parts = line[1:].strip().split("—", 1)
            key = parts[0].strip()
            val = parts[1].strip() if len(parts) > 1 else ""
            lines_svg += f'<text x="{padding}" y="{y}" font-family="{font_family}, sans-serif" font-size="13.5" fill="#cccccc"><tspan fill="#555">◦ </tspan><tspan font-weight="600" fill="#ffffff">{key}</tspan><tspan fill="#555"> — </tspan><tspan>{val}</tspan></text>\n'
        elif line.startswith("•"):
            text = line[1:].strip()
            lines_svg += f'<text x="{padding}" y="{y}" font-family="{font_family}, sans-serif" font-size="13.5" fill="#cccccc"><tspan fill="#555">• </tspan><tspan>{text}</tspan></text>\n'
        else:
            lines_svg += f'<text x="{padding}" y="{y}" font-family="{font_family}, sans-serif" font-size="13" fill="#888888">{line}</text>\n'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <style>{font_css}</style>
    {shadow_filter}
    <clipPath id="window-clip">
      <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="12" ry="12"/>
    </clipPath>
  </defs>

  <!-- Window -->
  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="12" ry="12" fill="#1e1e1e" {shadow_attr}/>

  <!-- Title bar -->
  <rect x="0" y="0" width="{WIDTH}" height="{title_bar_h}" rx="12" ry="12" fill="#2d2d2d"/>
  <rect x="0" y="22" width="{WIDTH}" height="16" fill="#2d2d2d"/>
  <line x1="0" y1="{title_bar_h}" x2="{WIDTH}" y2="{title_bar_h}" stroke="#3a3a3a" stroke-width="1"/>

  <!-- Traffic lights -->
  <circle cx="20" cy="19" r="6" fill="#ff5f57"/>
  <circle cx="40" cy="19" r="6" fill="#febc2e"/>
  <circle cx="60" cy="19" r="6" fill="#28c840"/>

  <!-- Title -->
  <text x="{WIDTH//2}" y="24" text-anchor="middle" font-family="{font_family}, sans-serif" font-size="13" fill="#888888">{title}</text>

  <!-- Content area bg -->
  <rect x="0" y="{title_bar_h}" width="{WIDTH}" height="{content_h}" fill="#1e1e1e" clip-path="url(#window-clip)"/>

  <!-- Banner bg -->
  <g clip-path="url(#window-clip)">
    {bg_svg}
  </g>

  <!-- Content -->
  <g clip-path="url(#window-clip)">
    {lines_svg}
  </g>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open(f"assets/{filename}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ assets/{filename}.svg generated!")

def main():
    # About Me
    generate_window("◈ About Me", [
        "Name — Fatur",
        "Age — 14 y/o 🎂",
        "Grade — 9th Grade, Junior High",
        "Focus — ROM Porting · Magisk Modules",
        "Status — Relaxed, productive when the mood strikes",
        'Motto — "Boy of 1000 dreams."',
    ], "window_about")

    # What do i like to do
    generate_window("◈ What do i like to do?", [
        "🔧 OEM Porting — like solving a puzzle that fights back",
        "🧩 Magisk Modules — bending android to my will, one module at a time",
        "📚 Trying Something New — scripts, banners, autoport & more",
    ], "window_whatido")

    # Stack
    generate_window("◈ Stack", [
        "🤖 Android — primary platform for ROM porting",
        "🖥️ Shell — scripting, automation & module building",
    ], "window_stack")

    # What's in my ears
    generate_window("◈ What's in my ears 🎶", [
        "genres i vibe with :",
        "◦ Pluggnb — dreamy trap meets jazzy R&B, layered synths and auto-tuned emotion",
        "◦ HipDut — raw street narratives in Dutch, hard-hitting bass with urban identity",
        "◦ Arabic Song — deeply emotional & cinematic, melodies that hit the soul",
        "◦ JJCore — high-speed Japanese hardcore, anime samples at max BPM",
        "◦ Vocaloid — synthetic voices carrying real emotions, from catchy pop to dark introspection",
        "◦ HyperPop — everything turned up to 11, glitchy chaos that refuses to conform",
    ], "window_ears")

if __name__ == "__main__":
    main()
