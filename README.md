# zerophyx-4

```
  ███████╗███████╗██████╗  ██████╗ ██████╗ ██╗  ██╗██╗   ██╗██╗  ██╗    ██╗  ██╗
  ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██║  ██║╚██╗ ██╔╝╚██╗██╔╝    ██║  ██║
    ███╔╝ █████╗  ██████╔╝██║   ██║██████╔╝███████║ ╚████╔╝  ╚███╔╝     ███████║
   ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██╔═══╝ ██╔══██║  ╚██╔╝   ██╔██╗     ╚════██║
  ███████╗███████╗██║  ██║╚██████╔╝██║     ██║  ██║   ██║   ██╔╝ ██╗         ██║
  ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝         ╚═╝
```

<div align="center">

*Just a quiet person with ideals that might be considered unique 🤠.*

</div>

---

<div align="center">

**`zerophyx-4`** — not lost, just got too many worlds to conquer.

<img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="180" />

</div>

---

## ◈ about

```yaml
name     : zerophyx-4
focus    : ROM Porting  ·  Magisk Modules
status   : Relaxed, Productive when the mood strikes
motto    : "Man of 1000 dreams."
```

---

## ◈ what i do

```
🔧  ROM Porting       →  like playing puzzle
🧩  Magisk Modules    →  bending android to my will
```

---

## ◈ stack

![Android](https://img.shields.io/badge/Android-000000?style=flat-square&logo=android&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-000000?style=flat-square&logo=linux&logoColor=white)
![Shell](https://img.shields.io/badge/Shell-000000?style=flat-square&logo=gnubash&logoColor=white)

---

## ◈ what's in my ears

```
genres i vibe with :

  ◦ Pluggnb          →  dark, melodic, heavy bass
  ◦ HipDut           →  dutch rap energy
  ◦ Arabic Song      →  emotional & cinematic
  ◦ JJCore           →  jujutsu kaisen-coded beats
  ◦ Vocaloid         →  synthetic soul
  ◦ HyperPop         →  chaotic and loud, just like my mind
```

---

## ◈ recently played

[![spotify](https://spotify-recently-played-readme.vercel.app/api?user=31zoke6ilfw7qgv42sxm6qnlxndu&count=5&width=400)](https://open.spotify.com)

> ⚠️ ganti `YOUR_SPOTIFY_USER_ID` dengan Spotify User ID kamu

---

## ◈ stats

<div align="center">

![zerophyx-4's GitHub Stats](https://github-readme-stats.vercel.app/api?username=zerophyx-4&show_icons=true&theme=github_dark&hide_border=true&bg_color=000000&title_color=ffffff&text_color=888888&icon_color=ffffff)

</div>

---

## ◈ contribution

<div align="center">

![Pacman](https://github.com/zerophyx-4/zerophyx-4/blob/output/github-contribution-grid-snake.svg)

</div>

---

<div align="center">

```
compiled in silence  ·  released among the stars
```

</div>

---

<details>
<summary>⚙️ setup pacman snake (klik untuk lihat)</summary>

buat file `.github/workflows/snake.yml` di repo ini, isi dengan:

```yaml
name: Generate Snake

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: zerophyx-4
          outputs: |
            dist/github-contribution-grid-snake.svg
            dist/github-contribution-grid-snake-dark.svg?palette=github-dark
      - uses: crazy-max/ghaction-github-pages@v3
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

lalu pergi ke tab **Actions** → run workflow-nya manual sekali.

</details>
