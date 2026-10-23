#!/usr/bin/env python3
"""Regenerate Video/index.html from the two mypleasurefilm YouTube playlists.

Run manually: python3 scripts/update_videos.py
Run automatically every Sunday via .github/workflows/update-videos.yml
"""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Video" / "index.html"
HEADER = ROOT / "shared" / "site-header.html"

PLAYLISTS = [
    {"id": "PLJlbT8Y-GAB4", "cat": "ad"},
    {"id": "PLFWsEnk1jmuc", "cat": "exhibit"},
]

NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

CAT_LABELS = {
    "all": "全部",
    "ad": "商業廣告製作",
    "exhibit": "展覽活動紀錄",
}


def fetch_playlist(playlist_id, cat):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    videos = []
    for entry in root.findall("a:entry", NS):
        vid = entry.find("yt:videoId", NS).text
        title = entry.find("a:title", NS).text
        videos.append({"id": vid, "title": title, "cat": cat})
    return videos


def build_card(v):
    vid = html.escape(v["id"], quote=True)
    title = html.escape(v["title"])
    cat = html.escape(v["cat"], quote=True)
    return f'''      <div class="card" data-cat="{cat}" data-id="{vid}">
        <div class="card-thumb">
          <img src="https://img.youtube.com/vi/{vid}/maxresdefault.jpg" alt="{title}" loading="lazy" />
          <div class="card-play"><div class="card-play-circle">&#9658;</div></div>
        </div>
        <div class="card-info">
          <div class="card-name">{title}</div>
        </div>
      </div>'''


def build_html(videos):
    header_html = HEADER.read_text(encoding="utf-8").rstrip()
    tabs_html = "\n".join(
        f'      <button class="tab{" active" if k == "all" else ""}" data-cat="{k}">{v}</button>'
        for k, v in CAT_LABELS.items()
    )
    cards_html = "\n".join(build_card(v) for v in videos)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Vincent Liao — Video</title>
<style>
  :root {{
    --bg: #0a0a0a;
    --surface: #141414;
    --text: #f2f2f2;
    --muted: #8a8a8a;
    --border: rgba(255,255,255,0.1);
    --accent: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'Helvetica Neue', Arial, 'Noto Sans TC', sans-serif;
    -webkit-font-smoothing: antialiased;
  }}


  .page {{ padding: 2.5rem 10% 6rem; }}

  .tabs {{
    display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap;
    margin-bottom: 2.5rem;
  }}
  .tab {{
    font-size: 0.78rem; letter-spacing: 0.12em;
    padding: 0.45rem 1.1rem; border: 1px solid var(--border); border-radius: 2px;
    background: none; color: var(--muted); cursor: pointer; transition: all 0.2s;
  }}
  .tab:hover, .tab.active {{ background: var(--accent); border-color: var(--accent); color: #000; }}

  .grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.4rem 1.1rem;
  }}
  @media (max-width: 1100px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); }} }}
  @media (max-width: 900px)  {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
  @media (max-width: 700px) {{
    .page {{ padding: 1.8rem 3% 4rem; }}
    .grid {{ grid-template-columns: repeat(2, 1fr); gap: 0.8rem; }}
  }}

  .card {{
    cursor: pointer; background: var(--surface);
  }}
  .card.hidden {{ display: none; }}
  .card-thumb {{ position: relative; aspect-ratio: 16/9; overflow: hidden; background: var(--surface); }}
  .card-thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.5s ease; }}
  .card:hover .card-thumb img {{ transform: scale(1.05); }}

  .card-play {{
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,0.35);
    opacity: 0; transition: opacity 0.3s;
  }}
  .card:hover .card-play {{ opacity: 1; }}
  .card-play-circle {{
    width: 52px; height: 52px;
    border: 2px solid #fff; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 1rem; padding-left: 3px;
  }}

  .card-info {{ padding: 3.3% 2%; }}
  .card-name {{ font-size: 0.88rem; letter-spacing: 0.03em; line-height: 1.4; text-indent: 0.5em; }}

  /* lightbox */
  .lb {{
    display: none; position: fixed; inset: 0; z-index: 9000;
    background: #000;
  }}
  .lb.open {{ display: block; }}
  .lb-inner {{
    position: absolute; inset: 0;
  }}
  .lb-inner iframe {{ width: 100%; height: 100%; border: 0; display: block; }}
  .lb-close {{
    position: fixed; top: 1.6rem; right: 2rem;
    background: none; border: none; color: #eee;
    cursor: pointer; font-size: 1.8rem; opacity: 0.6; transition: opacity 0.2s;
  }}
  .lb-close:hover {{ opacity: 1; }}
</style>
<link rel="stylesheet" href="../shared/site-header.css" />
<script src="../shared/site-header.js" defer></script>
</head>
<body>

{header_html}

  <div class="page">
    <div class="tabs">
{tabs_html}
    </div>

    <div class="grid" id="grid">
{cards_html}
    </div>
  </div>

  <div class="lb" id="lb">
    <button class="lb-close" id="lbClose">&times;</button>
    <div class="lb-inner"><iframe id="lbIframe" src="" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>
  </div>

<script>
  const tabs = document.querySelectorAll('.tab');
  const cards = document.querySelectorAll('.card');
  tabs.forEach(tab => {{
    tab.addEventListener('click', () => {{
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const cat = tab.dataset.cat;
      cards.forEach(card => {{
        const show = cat === 'all' || card.dataset.cat === cat;
        card.classList.toggle('hidden', !show);
      }});
    }});
  }});

  const lb = document.getElementById('lb');
  const lbIframe = document.getElementById('lbIframe');
  function openLb(id) {{
    lbIframe.src = `https://www.youtube.com/embed/${{id}}?autoplay=1`;
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }}
  function closeLb() {{
    lb.classList.remove('open');
    lbIframe.src = '';
    document.body.style.overflow = '';
  }}
  cards.forEach(card => {{
    card.addEventListener('click', () => openLb(card.dataset.id));
  }});
  document.getElementById('lbClose').addEventListener('click', closeLb);
  lb.addEventListener('click', (e) => {{ if (e.target === lb) closeLb(); }});
  document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeLb(); }});
</script>
</body>
</html>
"""


def main():
    all_videos = []
    for pl in PLAYLISTS:
        all_videos.extend(fetch_playlist(pl["id"], pl["cat"]))

    if not all_videos:
        raise SystemExit("No videos fetched from either playlist — aborting without writing.")

    output = build_html(all_videos)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Wrote {len(all_videos)} videos to {OUTPUT}")


if __name__ == "__main__":
    main()
