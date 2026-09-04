#!/usr/bin/env python3
"""Build all image assets for the FED-LINk repository.

Converts the generated base images into the exact files the approved
tree requires, then draws the architecture diagram and the animated
demo GIF. Runs OUTSIDE the project (assets land inside it).

Outputs (relative to the project root):
    docs/images/logo.png          (512x512, from the generated logo)
    docs/images/architecture.png  (matplotlib pipeline diagram)
    docs/images/demo.gif          (animated build -> redirect demo)
    social-image.png              (1200x630, root)
    assets/icon.png               (512x512)
    assets/icon.ico               (16/32/48/64/128/256)
    assets/icon.icns              (hand-built ICNS container)
"""

import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path("/workspace/infinityfree-shortener-builder")
GEN = Path("/workspace/generated_images")

LOGO_SRC = GEN / "generated_image_5a76bb4d-55be-493a-997e-faac757803ad_0.png"
ICON_SRC = GEN / "generated_image_b59f6ffc-da2b-450d-9db0-4386fc1b4800_0.png"
BANNER_SRC = GEN / "generated_image_a25cee48-ff42-4c29-97d2-4cbf4b30a189_0.png"

BG = (15, 17, 21)        # #0f1115
ACCENT = (122, 162, 247)  # #7aa2f7
FG = (224, 227, 234)     # light foreground
MUTED = (120, 126, 140)  # muted gray


def try_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def convert_static():
    """logo.png, social-image.png, icon.png, icon.ico."""
    (PROJECT / "docs/images").mkdir(parents=True, exist_ok=True)
    (PROJECT / "assets").mkdir(parents=True, exist_ok=True)

    # logo: center-crop to square, resize 512
    logo = Image.open(LOGO_SRC).convert("RGB")
    w, h = logo.size
    side = min(w, h)
    logo = logo.crop(((w - side) // 2, (h - side) // 2,
                      (w + side) // 2, (h + side) // 2)).resize((512, 512), Image.LANCZOS)
    logo.save(PROJECT / "docs/images/logo.png", optimize=True)

    # social image: 1200x630 center crop of the banner
    banner = Image.open(BANNER_SRC).convert("RGB")
    w, h = banner.size
    target_ratio = 1200 / 630
    if w / h > target_ratio:  # too wide -> crop width
        new_w = int(h * target_ratio)
        x = (w - new_w) // 2
        banner = banner.crop((x, 0, x + new_w, h))
    else:                     # too tall -> crop height
        new_h = int(w / target_ratio)
        y = (h - new_h) // 2
        banner = banner.crop((0, y, w, y + new_h))
    banner = banner.resize((1200, 630), Image.LANCZOS)
    banner.save(PROJECT / "social-image.png", optimize=True)

    # icon.png: 512x512
    icon = Image.open(ICON_SRC).convert("RGB")
    w, h = icon.size
    side = min(w, h)
    icon = icon.crop(((w - side) // 2, (h - side) // 2,
                      (w + side) // 2, (h + side) // 2)).resize((512, 512), Image.LANCZOS)
    icon.save(PROJECT / "assets/icon.png", optimize=True)

    # icon.ico: multi-size
    icon.save(PROJECT / "assets/icon.ico",
              sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def build_icns():
    """Hand-built ICNS: PNG-embedded ic07/ic09/ic10/ic11 chunks in a
    proper 'icns' container (works on modern macOS)."""
    icon = Image.open(PROJECT / "assets/icon.png").convert("RGBA")
    chunks = []
    for tag, size in ((b"ic07", 128), (b"ic09", 512), (b"ic10", 1024), (b"ic11", 32)):
        buf = icon.resize((size, size), Image.LANCZOS)
        import io
        bio = io.BytesIO()
        buf.save(bio, format="PNG")  # PNG-encoded payload
        png = bio.getvalue()
        chunks.append(tag + struct.pack(">I", len(png) + 8) + png)
    body = b"".join(chunks)
    with open(PROJECT / "assets/icon.icns", "wb") as fh:
        fh.write(b"icns" + struct.pack(">I", len(body) + 8) + body)


def draw_architecture():
    """docs/images/architecture.png — the build pipeline diagram."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(11, 5.4), dpi=150)
    fig.patch.set_facecolor("#0f1115")
    ax.set_facecolor("#0f1115")
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 54)
    ax.axis("off")

    def box(x, y, w, h, title, sub, face="#161a22", edge="#7aa2f7"):
        patch = FancyBboxPatch((x, y), w, h,
                               boxstyle="round,pad=0.6,rounding_size=1.2",
                               linewidth=1.4, edgecolor=edge, facecolor=face)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center",
                color="#e0e3ea", fontsize=10.5, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                color="#9aa2b1", fontsize=8.2)

    def arrow(x1, y1, x2, y2, label=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle="-|>", mutation_scale=14,
                                     linewidth=1.3, color="#7aa2f7"))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 1.4, label, ha="center",
                    color="#9aa2b1", fontsize=8)

    box(1.5, 33, 20, 13, "links.json / .yaml / .csv", "10 slugs -> destinations")
    box(27, 33, 18, 13, "parse", "src/parsers/")
    box(50.5, 33, 18, 13, "validate", "src/validators/\nslug + URL rules")
    box(74, 33, 18, 13, "generate", "src/generator/\nclean-first")
    box(1.5, 9, 20, 13, ".htaccess", "Redirect 301 /slug dest")
    box(27, 9, 18, 13, "index.html", "per-slug redirect pages")
    box(50.5, 9, 18, 13, "404.html + links.json", "fallback + manifest")
    box(74, 9, 18, 13, "links.zip", "deterministic package")

    arrow(21.5, 39.5, 27, 39.5)
    arrow(45, 39.5, 50.5, 39.5)
    arrow(68.5, 39.5, 74, 39.5)
    arrow(83, 33, 36, 22)      # generate -> the four artifacts
    arrow(83, 33, 60, 22)
    arrow(83, 33, 11.5, 22)
    arrow(60, 15.5, 74, 15.5, "pack")

    ax.text(55, 50.5, "FED-LINk build pipeline", ha="center", color="#e0e3ea",
            fontsize=13, fontweight="bold")
    ax.text(55, 3.2, "upload links.zip -> InfinityFree htdocs (link.fedpromptly.com)  |  CI mirrors output/ -> GitHub Pages",
            ha="center", color="#9aa2b1", fontsize=8.4)

    fig.savefig(PROJECT / "docs/images/architecture.png",
                facecolor="#0f1115", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def draw_demo():
    """docs/images/demo.gif — animated terminal-style build demo."""
    frames_text = [
        ("$ python -m src.main build configs/links.json --zip links.zip", 0.9),
        ("validating 10 links ................................ OK", 0.8),
        ("output/.htaccess      10 x Redirect 301", 0.8),
        ("output/portfolio/     -> fedpromptly.github.io/portfolio", 0.8),
        ("output/game/          -> fedpromptly.github.io/game", 0.8),
        ("output/docs/          -> fedpromptly.github.io/docs", 0.8),
        ("output/blog/  resume/ shop/  app/  tools/  contact/", 0.8),
        ("output/kofi/          -> ko-fi.com/fedpromptly", 0.8),
        ("packaged 13 file(s) into links.zip", 0.9),
        ("", 0.4),
        ("$ curl -sI https://link.fedpromptly.com/portfolio", 0.9),
        ("HTTP/1.1 301 Moved Permanently", 0.9),
        ("Location: https://fedpromptly.github.io/portfolio", 1.0),
    ]

    font = try_font(15)
    width, height = 760, 420
    frames = []
    lines = []

    for text, delay in frames_text:
        if text:
            lines.append(text)
        img = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(img)
        # title bar
        draw.rectangle([0, 0, width, 34], fill="#161a22")
        for i, color in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            draw.ellipse([16 + i * 22, 12, 28 + i * 22, 24], fill=color)
        draw.text((width // 2 - 60, 9), "FED-LINk", font=try_font(13, bold=True),
                  fill=FG)
        y = 52
        for line in lines:
            color = ACCENT if line.startswith("$") else FG
            if "301" in line or "OK" in line or "packaged" in line:
                color = (62, 200, 124)  # success green
            draw.text((18, y), line, font=font, fill=color)
            y += 24
        frames.append((img.copy(), int(delay * 1000)))

    # hold the final frame a bit longer
    frames.append((frames[-1][0].copy(), 1800))

    frames[0][0].save(PROJECT / "docs/images/demo.gif",
                      save_all=True,
                      append_images=[f[0] for f in frames[1:]],
                      duration=[f[1] for f in frames],
                      loop=0, optimize=True)


def main():
    convert_static()
    build_icns()
    draw_architecture()
    draw_demo()
    for path in ("docs/images/logo.png", "docs/images/architecture.png",
                 "docs/images/demo.gif", "social-image.png",
                 "assets/icon.png", "assets/icon.ico", "assets/icon.icns"):
        full = PROJECT / path
        print(f"{path:35s} {full.stat().st_size:>9,} bytes")


if __name__ == "__main__":
    main()
