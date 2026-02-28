import requests
import base64
import json
import os
import math

with open("friend-list.json", "r") as f:
    config = json.load(f)

FRIENDS        = config.get("friends", [])
TITLE          = config.get("title", "My Friend 😆🔥")
FONT_NAME      = config.get("font", "inter")
ROWS           = config.get("rows", 2)
ASKEW          = config.get("askew", 0)
DIRECTION      = config.get("direction", "</>")
ORDER          = config.get("order", [1, 3])
SLIDE          = config.get("slide", ">")
ROUNDED        = config.get("rounded_corner", 16)
BG             = config.get("background", {})
BG_IMAGE       = BG.get("image", "")
BG_BLUR        = BG.get("blur", 0)
BG_OPACITY     = BG.get("opacity", 1.0)
BG_MIRROR      = BG.get("mirror", False)

def get_avatar_base64(username):
    url = f"https://avatars.githubusercontent.com/{username}?size=80"
    r = requests.get(url)
    if r.status_code == 200:
        return base64.b64encode(r.content).decode("utf-8")
    return None

def get_file_base64(path):
    if not path or not os.path.exists(path):
        return None, None
    ext = path.split(".")[-1].lower()
    mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","gif":"image/gif"}.get(ext,"image/png")
    with open(path, "rb") as f:
        return mime, base64.b64encode(f.read()).decode("utf-8")

def fetch_google_font(font_name):
    try:
        import re
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

def get_animation(row_idx, row_width, card_width, duration):
    use_askew = ASKEW != 0 and DIRECTION != "</>"
    if ORDER == 0:
        goes_with = True
    else:
        goes_with = (row_idx + 1) in ORDER

    if use_askew:
        angle_rad = math.radians(ASKEW)
        dx = math.cos(angle_rad) * (card_width + row_width)
        dy = math.sin(angle_rad) * row_width * 0.3
        if DIRECTION == "/":
            fx, fy = (0, 0) if goes_with else (dx, dy)
            tx, ty = (-dx, -dy) if goes_with else (0, 0)
        else:
            fx, fy = (0, 0) if goes_with else (-dx, dy)
            tx, ty = (dx, -dy) if goes_with else (0, 0)
    else:
        if SLIDE == ">":
            fx, fy = (0, 0) if goes_with else (-row_width, 0)
            tx, ty = (row_width, 0) if goes_with else (0, 0)
        else:
            fx, fy = (0, 0) if goes_with else (row_width, 0)
            tx, ty = (-row_width, 0) if goes_with else (0, 0)

    return f"{fx},{fy}", f"{tx},{ty}"

def generate_svg(friends_data):
    item_width  = 140
    item_height = 145
    padding_top = 105
    padding_x   = 20

    total    = len(friends_data)
    per_row  = math.ceil(total / ROWS)
    rows_data = [friends_data[i:i+per_row] for i in range(0, total, per_row)]

    max_per_row = max(len(r) for r in rows_data)
    card_width  = max(520, max_per_row * item_width + padding_x * 2)
    svg_height  = len(rows_data) * item_height + padding_top + 20

    font_face, font_family = fetch_google_font(FONT_NAME)
    font_css = font_face if font_face else ""

    # Background layers
    bg_layers = ""

    # Mirror effect — pakai avatar sebagai background blur berlawanan arah
    if BG_MIRROR and friends_data:
        mirror_items = ""
        mirror_size  = 100
        mirror_cols  = card_width // mirror_size + 2
        mirror_rows  = svg_height // mirror_size + 2

        for ri in range(mirror_rows):
            for ci in range(mirror_cols):
                idx = (ri * mirror_cols + ci) % len(friends_data)
                av = friends_data[idx].get("avatar")
                if av:
                    # Baris genap gerak berlawanan dari baris ganjil
                    flip = -1 if ri % 2 == 0 else 1
                    mx = ci * mirror_size
                    my = ri * mirror_size
                    mirror_items += f'<image href="data:image/png;base64,{av}" x="{mx}" y="{my}" width="{mirror_size}" height="{mirror_size}" opacity="0.15"/>'

        bg_layers += f'''
        <filter id="mirror-blur"><feGaussianBlur stdDeviation="{max(BG_BLUR, 6)}"/></filter>
        <g filter="url(#mirror-blur)" opacity="{BG_OPACITY}">
          {mirror_items}
        </g>'''

    # Banner image
    if BG_IMAGE:
        mime, b64 = get_file_base64(BG_IMAGE)
        if b64:
            blur_attr   = f'filter="url(#banner-blur)"' if BG_BLUR > 0 else ""
            blur_filter = f'<filter id="banner-blur"><feGaussianBlur stdDeviation="{BG_BLUR}"/></filter>' if BG_BLUR > 0 else ""
            bg_layers  += f'{blur_filter}<image href="data:{mime};base64,{b64}" x="0" y="0" width="{card_width}" height="{svg_height}" preserveAspectRatio="xMidYMid slice" opacity="{BG_OPACITY}" {blur_attr}/>'

    defs_svg  = ""
    items_svg = ""

    for row_idx, row in enumerate(rows_data):
        if not row:
            continue

        row_width = len(row) * item_width
        y_offset  = row_idx * item_height
        duration  = 14 + row_idx * 2

        from_pos, to_pos = get_animation(row_idx, row_width, card_width, duration)

        # Seamless: buat 3 set konten (kiri, tengah, kanan) biar loop ga kedip
        sets = [-row_width, 0, row_width]
        items_inner = ""

        for offset_x in sets:
            for i, friend in enumerate(row):
                x        = i * item_width + padding_x + offset_x
                cx       = x + item_width // 2 - padding_x
                cy       = y_offset + 55
                uid      = f"r{row_idx}_s{offset_x}_i{i}".replace("-","n")
                username = friend["username"]
                gh_link  = f"https://github.com/{username}"
                avatar   = friend.get("avatar")

                defs_svg += f'<clipPath id="{uid}"><circle cx="{cx}" cy="{cy}" r="44"/></clipPath>'
                items_inner += f'<a href="{gh_link}" target="_blank">'
                if avatar:
                    items_inner += f'<image href="data:image/png;base64,{avatar}" x="{cx-44}" y="{cy-44}" width="88" height="88" clip-path="url(#{uid})"/>'
                else:
                    items_inner += f'<circle cx="{cx}" cy="{cy}" r="44" fill="#2a2a2a"/>'
                items_inner += f'<text x="{cx}" y="{y_offset+112}" text-anchor="middle" fill="#cccccc" font-size="11" font-family="{font_family}">@{username}</text>'
                items_inner += '</a>'

        items_svg += f'''
    <g>
      <animateTransform attributeName="transform" type="translate"
        from="{from_pos}" to="{to_pos}"
        dur="{duration}s" repeatCount="indefinite" calcMode="linear"/>
      {items_inner}
    </g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{card_width}" height="{svg_height}" viewBox="0 0 {card_width} {svg_height}">
  <defs>
    <style>{font_css}</style>
    {defs_svg}
    <clipPath id="card-clip">
      <rect x="0" y="0" width="{card_width}" height="{svg_height}" rx="{ROUNDED}" ry="{ROUNDED}"/>
    </clipPath>
  </defs>

  <!-- Card background -->
  <rect width="{card_width}" height="{svg_height}" rx="{ROUNDED}" ry="{ROUNDED}" fill="#0d0d0d"/>

  <!-- Background layers (mirror + banner) -->
  <g clip-path="url(#card-clip)">
    {bg_layers}
  </g>

  <!-- Title -->
  <text x="{card_width//2}" y="44" text-anchor="middle" fill="#ffffff"
    font-size="15" font-weight="bold" font-family="{font_family}">{TITLE}</text>

  <!-- Friends -->
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
    with open("assets/friends.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ friends.svg generated!")

if __name__ == "__main__":
    main()
