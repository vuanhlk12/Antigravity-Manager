#!/usr/bin/env python3
"""
Generate all Antigravity Manager app icons.
Uses the rainbow arch logo from the installed Antigravity.app on a dark
squircle background, with a Lucide Settings gear badge at the bottom-right.
"""

import os
import io
import ctypes.util

# Patch ctypes.util.find_library so cairocffi finds the Homebrew-installed cairo
# on macOS where DYLD_LIBRARY_PATH is stripped by SIP.
_CAIRO_BREW_PATH = "/opt/homebrew/lib/libcairo.2.dylib"
_orig_find_library = ctypes.util.find_library

def _patched_find_library(name):
    if name in ("cairo", "cairo-2", "libcairo-2") and os.path.exists(_CAIRO_BREW_PATH):
        return _CAIRO_BREW_PATH
    return _orig_find_library(name)

ctypes.util.find_library = _patched_find_library

import cairosvg  # noqa: E402 – must come after the patch
from PIL import Image  # noqa: E402

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'src-tauri', 'icons')

# Arch logo from the installed Antigravity.app (transparent background, 512×512)
APP_ARCH_ICNS = '/Applications/Antigravity.app/Contents/Resources/icon.icns'
APP_ARCH_ICONSET = '/tmp/antigravity_arch_extracted.iconset'

# ── Lucide Settings SVG badge ─────────────────────────────────────────────────
# viewBox 24×24 path data from lucide-react v0.561.0
GEAR_PATH = (
    "M9.671 4.136a2.34 2.34 0 0 1 4.659 0 "
    "2.34 2.34 0 0 0 3.319 1.915 "
    "2.34 2.34 0 0 1 2.33 4.033 "
    "2.34 2.34 0 0 0 0 3.831 "
    "2.34 2.34 0 0 1-2.33 4.033 "
    "2.34 2.34 0 0 0-3.319 1.915 "
    "2.34 2.34 0 0 1-4.659 0 "
    "2.34 2.34 0 0 0-3.32-1.915 "
    "2.34 2.34 0 0 1-2.33-4.033 "
    "2.34 2.34 0 0 0 0-3.831"
    "A2.34 2.34 0 0 1 6.35 6.051"
    "a2.34 2.34 0 0 0 3.319-1.915"
)

# Badge dimensions (will be scaled to badge_px × badge_px)
BADGE_PX = 235

# Colors
BG_COLOR      = "#090912"      # badge circle background (near-black)
BORDER_COLOR  = "#1E2D3D"      # subtle border
GEAR_COLOR    = "#F59E0B"      # amber – warm contrast vs blue/purple logo
GEAR_WIDTH    = "1.8"          # stroke-width inside 24×24 viewBox


def remove_white_bg(img: Image.Image, threshold: int = 225) -> Image.Image:
    """
    Remove white background from the Antigravity arch icon.
    Strategy: pixels where ALL of R,G,B > threshold become transparent.
    The background is 255,255,255 while the arch has at least one channel
    well below this (e.g. blue legs: R≈100, red top: G/B≈50).
    """
    import numpy as np

    data = np.array(img.convert('RGBA'), dtype=np.uint32)
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
    a = data[:, :, 3]
    bg_mask = (a > 0) & (r > threshold) & (g > threshold) & (b > threshold)
    data[bg_mask, 3] = 0
    return Image.fromarray(data.astype(np.uint8), 'RGBA')


def extract_arch_png(size: int = 512) -> Image.Image:
    """Extract the arch logo from the installed Antigravity.app icns file."""
    import subprocess
    os.makedirs(APP_ARCH_ICONSET, exist_ok=True)
    subprocess.run(
        ['iconutil', '-c', 'iconset', APP_ARCH_ICNS, '-o', APP_ARCH_ICONSET],
        check=True
    )
    # Pick the best available size
    for name in ['icon_512x512.png', 'icon_256x256@2x.png',
                  'icon_256x256.png', 'icon_128x128@2x.png']:
        path = os.path.join(APP_ARCH_ICONSET, name)
        if os.path.exists(path):
            img = Image.open(path).convert('RGBA')
            print(f'  Arch source: {name} ({img.size})')
            # Remove the white rounded-square background from the app icon
            img = remove_white_bg(img, threshold=230)
            return img
    raise FileNotFoundError('Could not extract arch icon from Antigravity.app')


def make_squircle_bg(size: int, margin: int = 0) -> Image.Image:
    """
    Dark squircle on a transparent canvas.
    margin: transparent border (px) around the squircle on each side.
    margin=0 → squircle edge-to-edge (transparent corners only from radius).
    """
    from PIL import ImageDraw
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    inner = size - 2 * margin
    r = int(inner * 0.225)
    draw.rounded_rectangle(
        [margin, margin, size - 1 - margin, size - 1 - margin],
        radius=r,
        fill=(13, 15, 26, 255),   # #0D0F1A deep navy-black
    )
    return img


def make_opaque_bg(size: int) -> Image.Image:
    """Solid opaque dark background (for Windows Square logos / 64x64)."""
    return Image.new('RGBA', (size, size), (13, 15, 26, 255))


def _place_arch(base: Image.Image, arch: Image.Image,
                inner_x: int, inner_y: int, inner_size: int) -> Image.Image:
    """Scale and centre arch within the squircle inner area, shifted up for badge."""
    arch_w = int(inner_size * 0.78)
    arch_h = int(arch.height * arch_w / arch.width)
    arch_r = arch.resize((arch_w, arch_h), Image.LANCZOS)
    x = inner_x + (inner_size - arch_w) // 2
    y = inner_y + int((inner_size - arch_h) * 0.36)
    base.paste(arch_r, (x, y), arch_r)
    return base


def build_master(arch: Image.Image, size: int = 1024,
                 margin: int = 0) -> Image.Image:
    """
    Build master icon: squircle + arch.
    margin > 0  → transparent border around squircle (macOS padded style).
    margin = 0  → squircle edge-to-edge (transparent corners only).
    """
    base = make_squircle_bg(size, margin)
    inner = size - 2 * margin
    return _place_arch(base, arch, margin, margin, inner)


def build_opaque(arch: Image.Image, size: int = 1024) -> Image.Image:
    """Build full-opaque icon (no transparency anywhere) for Windows Square logos."""
    base = make_opaque_bg(size)
    return _place_arch(base, arch, 0, 0, size)


def make_badge_svg(size: int) -> str:
    """Return SVG string for the gear badge at given pixel size."""
    half = size / 2
    r = half - 2          # circle radius (leave 2px for stroke)
    icon_margin = size * 0.17   # margin around the lucide icon area
    icon_x = icon_margin
    icon_y = icon_margin
    icon_dim = size - 2 * icon_margin

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <!-- badge background -->
  <circle cx="{half}" cy="{half}" r="{r:.1f}"
          fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="3"/>
  <!-- lucide settings icon, nested SVG keeps stroke-width clean -->
  <svg x="{icon_x:.1f}" y="{icon_y:.1f}"
       width="{icon_dim:.1f}" height="{icon_dim:.1f}"
       viewBox="0 0 24 24">
    <path d="{GEAR_PATH}"
          fill="none" stroke="{GEAR_COLOR}"
          stroke-width="{GEAR_WIDTH}"
          stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="12" cy="12" r="3"
            fill="none" stroke="{GEAR_COLOR}"
            stroke-width="{GEAR_WIDTH}"
            stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</svg>"""


def composite_badge(base: Image.Image, badge_px: int,
                    padding: int, squircle_margin: int = 0) -> Image.Image:
    """
    Render SVG badge and composite onto base image.
    squircle_margin: canvas-edge inset of the squircle, so the badge is
    positioned relative to the squircle's inner bottom-right corner.
    """
    svg_str = make_badge_svg(badge_px)
    png_data = cairosvg.svg2png(bytestring=svg_str.encode(),
                                output_width=badge_px, output_height=badge_px)
    badge = Image.open(io.BytesIO(png_data)).convert("RGBA")

    result = base.copy().convert("RGBA")
    w, h = result.size
    x = w - squircle_margin - badge_px - padding
    y = h - squircle_margin - badge_px - padding
    result.paste(badge, (x, y), badge)
    return result


def save(img: Image.Image, path: str, size: tuple[int, int]):
    resized = img.resize(size, Image.LANCZOS)
    resized.save(path, "PNG", optimize=True)
    print(f"  {os.path.basename(path):30s} {size[0]}×{size[1]}")


# Transparent padding around squircle for macOS icons (matches original ~10%)
MACOS_MARGIN = round(1024 * 0.098)   # ≈ 100 px for 1024×1024


def main():
    # ── 1. Extract arch logo from installed Antigravity.app ─────────────────
    print("Extracting arch logo from Antigravity.app…")
    arch = extract_arch_png()

    # ── 2a. macOS master: squircle WITH ~10% transparent padding ─────────────
    print("Building macOS master (with transparent padding)…")
    master_macos = build_master(arch, 1024, margin=MACOS_MARGIN)
    icon_macos = composite_badge(master_macos, BADGE_PX,
                                  padding=20, squircle_margin=MACOS_MARGIN)

    # ── 2b. Edge-to-edge squircle master (32×32 style) ───────────────────────
    print("Building edge-to-edge squircle master…")
    master_edge = build_master(arch, 1024, margin=0)
    icon_edge = composite_badge(master_edge, BADGE_PX, padding=20)

    # ── 2c. Opaque fill master (Windows Square logos / 64×64) ────────────────
    print("Building opaque fill master…")
    master_opaque = build_opaque(arch, 1024)
    icon_opaque = composite_badge(master_opaque, BADGE_PX, padding=20)

    print("\nWriting icons:")

    # ── 3. macOS icons (squircle with transparent padding) ───────────────────
    icon_path = os.path.join(ICONS_DIR, "icon.png")
    icon_macos.save(icon_path, "PNG", optimize=True)
    print(f"  {'icon.png':30s} 1024×1024  (padded squircle)")

    save(icon_macos, os.path.join(ICONS_DIR, "128x128.png"),    (128, 128))
    save(icon_macos, os.path.join(ICONS_DIR, "128x128@2x.png"), (256, 256))

    # ── 4. 32×32: squircle edge-to-edge (transparent corners only) ──────────
    save(icon_edge,  os.path.join(ICONS_DIR, "32x32.png"),  (32, 32))

    # ── 5. 64×64 and Windows Square logos: full opaque ───────────────────────
    save(icon_opaque, os.path.join(ICONS_DIR, "64x64.png"),  (64, 64))
    for name, sz in [
        ("Square30x30Logo.png",  (30,  30)),
        ("Square44x44Logo.png",  (44,  44)),
        ("Square71x71Logo.png",  (71,  71)),
        ("Square89x89Logo.png",  (89,  89)),
        ("Square107x107Logo.png",(107, 107)),
        ("Square142x142Logo.png",(142, 142)),
        ("Square150x150Logo.png",(150, 150)),
        ("Square284x284Logo.png",(284, 284)),
        ("Square310x310Logo.png",(310, 310)),
        ("StoreLogo.png",        (50,  50)),
    ]:
        save(icon_opaque, os.path.join(ICONS_DIR, name), sz)

    # ── 6. Tray icon: 44×44, arch only, transparent bg, 4px padding, no badge
    tray_size = 44
    tray_pad  = 4
    inner_sz  = tray_size - 2 * tray_pad
    tray_arch_w = inner_sz
    tray_arch_h = int(arch.height * tray_arch_w / arch.width)
    if tray_arch_h > inner_sz:
        tray_arch_h = inner_sz
        tray_arch_w = int(arch.width * tray_arch_h / arch.height)
    tray_arch = arch.resize((tray_arch_w, tray_arch_h), Image.LANCZOS)
    tray = Image.new('RGBA', (tray_size, tray_size), (0, 0, 0, 0))
    tx = tray_pad + (inner_sz - tray_arch_w) // 2
    ty = tray_pad + (inner_sz - tray_arch_h) // 2
    tray.paste(tray_arch, (tx, ty), tray_arch)
    tray.save(os.path.join(ICONS_DIR, "tray-icon.png"), "PNG", optimize=True)
    print(f"  {'tray-icon.png':30s} 44×44  (transparent, no badge)")

    # ── 7. .icns via iconset (macOS padded style) ────────────────────────────
    print("\nBuilding .icns …")
    iconset_dir = os.path.join(ICONS_DIR, "icon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    icns_sizes = [
        ("icon_16x16.png",       (16,  16)),
        ("icon_16x16@2x.png",    (32,  32)),
        ("icon_32x32.png",       (32,  32)),
        ("icon_32x32@2x.png",    (64,  64)),
        ("icon_64x64.png",       (64,  64)),
        ("icon_64x64@2x.png",    (128, 128)),
        ("icon_128x128.png",     (128, 128)),
        ("icon_128x128@2x.png",  (256, 256)),
        ("icon_256x256.png",     (256, 256)),
        ("icon_256x256@2x.png",  (512, 512)),
        ("icon_512x512.png",     (512, 512)),
        ("icon_512x512@2x.png",  (1024, 1024)),
    ]
    for fname, sz in icns_sizes:
        save(icon_macos, os.path.join(iconset_dir, fname), sz)

    icns_path = os.path.join(ICONS_DIR, "icon.icns")
    ret = os.system(f'iconutil -c icns "{iconset_dir}" -o "{icns_path}"')
    if ret == 0:
        print(f"  icon.icns generated ✓")
    else:
        print(f"  WARNING: iconutil failed (exit {ret})")

    print("\nDone.")


if __name__ == "__main__":
    main()
