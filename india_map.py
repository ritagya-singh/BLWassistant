"""
india_map.py — loads the real India SVG map from VictorCazanave/svg-maps
Used by app.py to embed a geographically accurate India outline as background.
"""
import urllib.request
import re
import os
_CACHE_FILE = os.path.join(os.path.dirname(__file__), "india_map_svg.txt")
def get_india_svg() -> str:
    """
    Returns the complete <svg>...</svg> string for the India map.
    Loads from cached file if available, otherwise fetches from GitHub.
    """
    if os.path.exists(_CACHE_FILE):
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    # Fetch from GitHub
    url = "https://raw.githubusercontent.com/VictorCazanave/svg-maps/master/packages/india/india.svg"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            content = r.read().decode("utf-8")
    except Exception as e:
        return _FALLBACK_SVG
    # Extract all real path d= values (> 50 chars = actual path data, not IDs)
    all_d_values = []
    for m in re.finditer(r'd="([^"]{50,})"', content):
        all_d_values.append(m.group(1))
    if not all_d_values:
        return _FALLBACK_SVG
    svg_lines = [
        '<svg viewBox="0 0 612 696" xmlns="http://www.w3.org/2000/svg">',
        '  <g fill="#0d3320">',

    ]
    for d in all_d_values:
        svg_lines.append(f'    <path d="{d}"/>')
    svg_lines.append("  </g>")
    svg_lines.append("</svg>")
    result = "\n".join(svg_lines)
    # Cache it for future runs
    try:
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(result)
    except Exception:
        pass
    return result
# Simple fallback if network is unavailable
_FALLBACK_SVG = """
<svg viewBox="0 0 612 696" xmlns="http://www.w3.org/2000/svg">
  <path fill="#2d6a4f" d="
    M 220,20 C 250,15 290,14 325,22 C 360,30 390,45 415,58
    C 445,72 470,90 485,108 C 495,122 494,138 488,154
    C 496,162 500,178 493,196 C 486,214 473,220 468,234
    C 460,252 455,270 446,288 C 436,308 424,328 412,348
    C 398,372 383,396 369,418 C 358,436 348,452 342,464
    C 336,476 332,480 330,472 C 323,454 314,434 302,412
    C 288,388 274,362 260,336 C 246,310 234,282 222,256
    C 208,230 208,230 208,230 C 198,210 180,222 158,244
    C 142,260 139,278 153,287 C 167,296 183,284 195,268
    C 203,256 206,242 203,230 C 200,215 191,192 185,168
    C 177,142 175,116 178,92 C 181,70 191,55 203,42
    C 215,30 218,25 220,20 Z
  "/>
</svg>
"""
