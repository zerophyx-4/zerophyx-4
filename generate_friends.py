import requests
import base64
import os

FRIENDS = [
    {"username": "XTENSEI"},
    {"username": "jvaswb"},
    {"username": "Greeezzz"},
    {"username": "KimelaZX"},
]

def get_avatar_base64(username):
    url = f"https://avatars.githubusercontent.com/{username}?size=80"
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    return None

def generate_svg(friends_data):
    card_width = 520
    item_width = 120
    item_height = 110
    rows = [
        friends_data[0:2],   # baris 1 (geser ke kanan)
        friends_data[2:4],   # baris 2 (geser ke kiri)
    ]

    row_directions = ["right", "left"]
    row_colors = ["#1a1a2e", "#16213e"]

    items_svg = ""
    animations_svg = ""

    for row_idx, (row, direction) in enumerate(zip(rows, row_directions)):
        if not row:
            continue

        total_width = len(row) * item_width
        y_offset = row_idx * item_height
        duration = 12 + row_idx * 2

        from_x = 0 if direction == "right" else -(total_width)
        to_x = total_width if direction == "right" else 0

        group_id = f"row{row_idx}"
        items_inner = ""

        for i, friend in enumerate(row):
            x = i * item_width
            avatar_b64 = friend.get("avatar")
            img_tag = ""
            if avatar_b64:
                img_tag = f'<image href="data:image/png;base64,{avatar_b64}" x="{x + 20}" y="{y_offset + 8}" width="80" height="80" clip-path="url(#circle{row_idx}_{i})" />'
                items_inner += f'<clipPath id="circle{row_idx}_{i}"><circle cx="{x + 60}" cy="{y_offset + 48}" r="40"/></clipPath>'
            else:
                items_inner += f'<circle cx="{x + 60}" cy="{y_offset + 48}" r="40" fill="#333"/>'

            items_inner += img_tag
            items_inner += f'<text x="{x + 60}" y="{y_offset + 100}" text-anchor="middle" fill="#ffffff" font-size="11" font-family="monospace">@{friend["username"]}</text>'

        items_svg += f'''
        <g id="{group_id}">
            {items_inner}
            <animateTransform attributeName="transform" type="translate"
                from="{from_x},0" to="{to_x},0"
                dur="{duration}s" repeatCount="indefinite"/>
        </g>'''

    svg_height = len(rows) * item_height + 50

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{card_width}" height="{svg_height}" viewBox="0 0 {card_width} {svg_height}">
  <defs>
    <style>
      text {{ font-family: monospace; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{svg_height}" rx="12" fill="#0d0d0d"/>

  <!-- Title -->
  <text x="{card_width // 2}" y="30" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="bold" font-family="monospace">My Friend 😆🔥</text>

  <!-- Clip to card -->
  <clipPath id="card-clip">
    <rect x="0" y="40" width="{card_width}" height="{svg_height - 40}" rx="8"/>
  </clipPath>

  <g clip-path="url(#card-clip)" transform="translate(0, 40)">
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
