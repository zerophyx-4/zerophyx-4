import requests
import base64
import json
import os
import math

# Baca config dari friend-list.json
with open("friend-list.json", "r") as f:
    config = json.load(f)

FRIENDS = config.get("friends", [])
TITLE   = config.get("title", "My Friend 😆🔥")
FONT    = config.get("font", "monospace")
ROWS    = config.get("rows", 2)

def get_avatar_base64(username):
    url = f"https://avatars.githubusercontent.com/{username}?size=80"
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    return None

def generate_svg(friends_data):
    card_width  = 520
    item_height = 115

    # Bagi teman ke sejumlah baris yang ditentukan di config
    total       = len(friends_data)
    per_row     = math.ceil(total / ROWS)
    rows        = [friends_data[i:i + per_row] for i in range(0, total, per_row)]
    row_dirs    = ["right", "left", "right"]

    defs_svg  = ""
    items_svg = ""

    for row_idx, row in enumerate(rows):
        if not row:
            continue

        direction   = row_dirs[row_idx % len(row_dirs)]
        item_width  = card_width // len(row)
        total_width = len(row) * item_width
        y_offset    = row_idx * item_height
        duration    = 12 + row_idx * 2

        from_x = -total_width if direction == "right" else total_width
        to_x   = card_width + total_width if direction == "right" else -(card_width + total_width)

        items_inner = ""

        for i, friend in enumerate(row):
            x        = i * item_width
            cx       = x + item_width // 2
            clip_id  = f"c{row_idx}_{i}"
            username = friend["username"]
            gh_link  = f"https://github.com/{username}"
            avatar_b64 = friend.get("avatar")

            defs_svg += f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{y_offset + 45}" r="38"/></clipPath>'

            # Wrap semua elemen teman dalam <a> biar bisa diklik
            items_inner += f'<a href="{gh_link}" target="_blank">'

            if avatar_b64:
                items_inner += f'<image href="data:image/png;base64,{avatar_b64}" x="{cx - 38}" y="{y_offset + 7}" width="76" height="76" clip-path="url(#{clip_id})" />'
            else:
                items_inner += f'<circle cx="{cx}" cy="{y_offset + 45}" r="38" fill="#2a2a2a"/>'

            items_inner += f'<text x="{cx}" y="{y_offset + 100}" text-anchor="middle" fill="#cccccc" font-size="11" font-family="{FONT}">@{username}</text>'
            items_inner += '</a>'

        items_svg += f'''
    <g>
      <animateTransform attributeName="transform" type="translate"
        from="{from_x},0" to="{to_x},0"
        dur="{duration}s" repeatCount="indefinite"/>
      {items_inner}
    </g>'''

    svg_height = len(rows) * item_height + 55

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{card_width}" height="{svg_height}" viewBox="0 0 {card_width} {svg_height}">
  <defs>
    {defs_svg}
    <clipPath id="card-clip">
      <rect x="0" y="44" width="{card_width}" height="{svg_height - 44}"/>
    </clipPath>
  </defs>

  <rect width="{card_width}" height="{svg_height}" rx="12" fill="#0d0d0d"/>

  <text x="{card_width // 2}" y="32" text-anchor="middle" fill="#ffffff"
    font-size="15" font-weight="bold" font-family="{FONT}">{TITLE}</text>

  <g clip-path="url(#card-clip)" transform="translate(0,44)">
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
