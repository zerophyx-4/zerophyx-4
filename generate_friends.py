import requests
import base64
import json
import os
import math

# Baca config dari friend-list.json
with open("friend-list.json", "r") as f:
    config = json.load(f)

FRIENDS   = config.get("friends", [])
TITLE     = config.get("title", "My Friend 😆🔥")
FONT_NAME = config.get("font", "inter")
ROWS      = config.get("rows", 2)
ASKEW     = config.get("askew", 0)
DIRECTION = config.get("direction", "</>")
ORDER     = config.get("order", [1, 3])
SLIDE     = config.get("slide", ">")
BG_IMAGE  = config.get("background", {}).get("image", "")
BG_BLUR   = config.get("background", {}).get("blur", 0)

def get_avatar_base64(username):
    url = f"https://avatars.githubusercontent.com/{username}?size=80"
    r = requests.get(url)
    if r.status_code == 200:
        return base64.b64encode(r.content).decode("utf-8")
    return None

def get_bg_base64(path):
    if not path or not os.path.exists(path):
        return None
    ext = path.split(".")[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
    with open(path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode("utf-8")

def fetch_google_font(font_name):
    """Fetch and embed Google Font as base64"""
    try:
        # Convert font name to Google Fonts API format
        api_name = font_name.replace(" ", "+").title()
        url = f"https://fonts.googleapis.com/css2?family={api_name}&display=swap"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None, font_name
        # Extract font URL from CSS
        import re
        font_urls = re.findall(r'url\((https://fonts\.gstatic\.com[^)]+)\)', r.text)
        if not font_urls:
            return None, font_name
        # Download font
        font_r = requests.get(font_urls[0])
        if font_r.status_code != 200:
            return None, font_name
        font_b64 = base64.b64encode(font_r.content).decode("utf-8")
        font_face = f"""@font-face {{
            font-family: '{font_name}';
            src: url('data:font/woff2;base64,{font_b64}') format('woff2');
        }}"""
        return font_face, font_name
    except:
        return None, font_name

def get_slide_transform(row_idx, row_width, card_width):
    """Calculate animation direction based on config"""
    use_askew = ASKEW != 0 and DIRECTION != "</>"

    if use_askew:
        # Mode miring
        angle_rad = math.radians(ASKEW)
        dx = math.cos(angle_rad) * (card_width + row_width)
        dy = math.sin(angle_rad) * (card_width + row_width)

        # Tentukan apakah baris ini ikut direction atau berlawanan
        if ORDER == 0:
            # Semua satu arah
            goes_with = True
        else:
            goes_with = (row_idx + 1) in ORDER

        if DIRECTION == "/":
            # / = kiri: from kanan ke kiri
            if goes_with:
                return f"0,0", f"{-dx},{-dy}"
            else:
                return f"0,0", f"{dx},{dy}"
        else:
            # \ = kanan
            if goes_with:
                return f"0,0", f"{dx},{-dy}"
            else:
                return f"0,0", f"{-dx},{dy}"
    else:
        # Mode datar
        if ORDER == 0:
            goes_with = True
        else:
            goes_with = (row_idx + 1) in ORDER

        if SLIDE == ">":
            if goes_with:
                return f"0,0", f"{row_width},0"
            else:
                return f"0,0", f"{-row_width},0"
        else:
            if goes_with:
                return f"0,0", f"{-row_width},0"
            else:
                return f"0,0", f"{row_width},0"

def generate_svg(friends_data):
    item_width  = 140
    item_height = 140
    padding_top = 100
    padding_x   = 20

    total    = len(friends_data)
    per_row  = math.ceil(total / ROWS)
    rows     = [friends_data[i:i + per_row] for i in range(0, total, per_row)]

    max_per_row = max(len(r) for r in rows)
    card_width  = max(520, max_per_row * item_width + padding_x * 2)
    svg_height  = len(rows) * item_height + padding_top + 20

    # Font
    font_face, font_family = fetch_google_font(FONT_NAME)
    font_css = font_face if font_face else ""

    # Background
    bg_svg = ""
    bg_result = get_bg_base64(BG_IMAGE)
    if bg_result:
        bg_mime, bg_b64 = bg_result
        blur_filter = f'<filter id="bg-blur"><feGaussianBlur stdDeviation="{BG_BLUR}"/></filter>' if BG_BLUR > 0 else ""
        blur_attr = 'filter="url(#bg-blur)"' if BG_BLUR > 0 else ""
        bg_svg = f'{blur_filter}<image href="data:{bg_mime};base64,{bg_b64}" x="0" y="0" width="{card_width}" height="{svg_height}" preserveAspectRatio="xMidYMid slice" {blur_attr}/>'

    defs_svg  = ""
    items_svg = ""

    for row_idx, row in enumerate(rows):
        if not row:
            continue

        row_width  = len(row) * item_width
        y_offset   = row_idx * item_height
        duration   = 14 + row_idx * 2

        from_pos, to_pos = get_slide_transform(row_idx, row_width, card_width)

        items_inner = ""
        items_dup   = ""

        for i, friend in enumerate(row):
            x        = i * item_width + padding_x
            cx       = x + item_width // 2 - padding_x
            cy       = y_offset + 60
            clip_id  = f"c{row_idx}_{i}"
            clip_dup = f"cd{row_idx}_{i}"
            username = friend["username"]
            gh_link  = f"https://github.com/{username}"
            avatar   = friend.get("avatar")

            # Original
            defs_svg += f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="44"/></clipPath>'
            items_inner += f'<a href="{gh_link}" target="_blank">'
            if avatar:
                items_inner += f'<image href="data:image/png;base64,{avatar}" x="{cx-44}" y="{cy-44}" width="88" height="88" clip-path="url(#{clip_id})"/>'
            else:
                items_inner += f'<circle cx="{cx}" cy="{cy}" r="44" fill="#2a2a2a"/>'
            items_inner += f'<text x="{cx}" y="{y_offset + 118}" text-anchor="middle" fill="#cccccc" font-size="11" font-family="{font_family}">@{username}</text>'
            items_inner += '</a>'

            # Duplikat untuk seamless loop
            cx2 = cx + row_width
            defs_svg += f'<clipPath id="{clip_dup}"><circle cx="{cx2}" cy="{cy}" r="44"/></clipPath>'
            items_dup += f'<a href="{gh_link}" target="_blank">'
            if avatar:
                items_dup += f'<image href="data:image/png;base64,{avatar}" x="{cx2-44}" y="{cy-44}" width="88" height="88" clip-path="url(#{clip_dup})"/>'
            else:
                items_dup += f'<circle cx="{cx2}" cy="{cy}" r="44" fill="#2a2a2a"/>'
            items_dup += f'<text x="{cx2}" y="{y_offset + 118}" text-anchor="middle" fill="#cccccc" font-size="11" font-family="{font_family}">@{username}</text>'
            items_dup += '</a>'

        items_svg += f'''
    <g>
      <animateTransform attributeName="transform" type="translate"
        from="{from_pos}" to="{to_pos}"
        dur="{duration}s" repeatCount="indefinite" calcMode="linear"/>
      {items_inner}
      {items_dup}
    </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{card_width}" height="{svg_height}" viewBox="0 0 {card_width} {svg_height}">
  <defs>
    <style>
      {font_css}
    </style>
    {defs_svg}
    <clipPath id="card-clip">
      <rect x="0" y="0" width="{card_width}" height="{svg_height}"/>
    </clipPath>
  </defs>

  <rect width="{card_width}" height="{svg_height}" rx="12" fill="#0d0d0d"/>
  {bg_svg}

  <text x="{card_width // 2}" y="44" text-anchor="middle" fill="#ffffff"
    font-size="15" font-weight="bold" font-family="{font_family}">{TITLE}</text>

  <g clip-path="url(#card-clip)" transform="translate(0,{padding_top})">
    {items_svg}
  </g>
</svg>'''

    return svg

def main():
    friends_data = []
    for f in FRIENDS:
        print(f"Fetching avatar for {f['username']}...")
        avatar = get_avatar_base64(f["username"])
        friends_data.append({"username": f["username"], "avatar": avatar})

    svg = generate_svg(friends_data)

    os.makedirs("assets", exist_ok=True)
    with open("assets/friends.svg", "w", encoding="utf-8") as file:
        file.write(svg)

    print("✅ friends.svg generated!")

if __name__ == "__main__":
    main()
