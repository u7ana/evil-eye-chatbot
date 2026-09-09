"""Generates the EE promo poster (1080x1080) with a QR code to the live site.
Run: python make_poster.py
Output: promo/ee_poster.png
"""
import math
import os

import arabic_reshaper
import qrcode
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---- Brand tokens (from client/tailwind.config.js + client/src/index.css) ----
PINE = (30, 81, 40)      # #1e5128
MOSS = (107, 155, 78)    # #6b9b4e
SAGE = (148, 184, 119)   # #94b877
CREAM = (242, 245, 232)  # #f2f5e8
INKG = (16, 51, 27)      # #10331b
SIDE = (22, 56, 31)      # #16381f - deep pine sidebar
WHITE = (255, 255, 255)

SITE_URL = "https://evil-eye-chatbot.vercel.app/"

W = H = 1080

FONT_DIR = r"C:\Windows\Fonts"
ARABIC_FONT = os.path.join(FONT_DIR, "segoeuib.ttf")   # bold, clean Arabic shaping
ARABIC_FONT_REG = os.path.join(FONT_DIR, "segoeui.ttf")
LOGO_FONT = os.path.join(FONT_DIR, "georgiab.ttf") if os.path.exists(
    os.path.join(FONT_DIR, "georgiab.ttf")
) else os.path.join(FONT_DIR, "arialbd.ttf")


def ar(text):
    """Reshape + reorder Arabic so PIL draws connected, correctly-ordered glyphs."""
    return get_display(arabic_reshaper.reshape(text))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size, top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = lerp(top, bottom, t)
        for x in range(w):
            px[x, y] = c
    return img


def draw_centered_text(draw, xy_center, text, font, fill, max_width=None, line_spacing=1.25):
    """Draws (already-shaped) text centered horizontally at xy_center, wrapping
    on spaces of the ORIGINAL logical string is not attempted here - callers
    pass one line at a time for simplicity/reliability with reshaped Arabic."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = xy_center[0] - tw / 2 - bbox[0]
    y = xy_center[1] - th / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=fill)
    return th


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_eye_pin(size):
    """Recreates the app's pin+eye brand mark (see client EyeLogo.jsx Rings)
    as a standalone RGBA image, drawn at high supersampled res then downscaled
    for clean anti-aliasing."""
    ss = 4
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = s / 2
    head_r = s * 0.34
    head_cy = s * 0.36

    # Pin head (pine circle)
    d.ellipse(
        [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
        fill=PINE,
    )
    # Pin tail (triangle down to a point), pine, blended into the head circle
    tail_top_half_w = head_r * 0.86
    tail_top_y = head_cy + head_r * 0.55
    tail_tip = (cx, s * 0.94)
    d.polygon(
        [
            (cx - tail_top_half_w, tail_top_y),
            (cx + tail_top_half_w, tail_top_y),
            tail_tip,
        ],
        fill=PINE,
    )

    # Eye rings, centered in the head circle
    ecy = head_cy
    for r, col in (
        (head_r * 0.74, MOSS),
        (head_r * 0.54, CREAM),
        (head_r * 0.36, SAGE),
        (head_r * 0.19, INKG),
    ):
        d.ellipse([cx - r, ecy - r, cx + r, ecy + r], fill=col)

    # Highlight dot
    hl_r = head_r * 0.055
    hl_dx, hl_dy = head_r * 0.09, -head_r * 0.08
    d.ellipse(
        [cx + hl_dx - hl_r, ecy + hl_dy - hl_r, cx + hl_dx + hl_r, ecy + hl_dy + hl_r],
        fill=WHITE,
    )

    img = img.resize((size, size), Image.LANCZOS)
    return img


def make_qr(url, box_px, dark=INKG, light=CREAM):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#%02x%02x%02x" % dark, back_color="#%02x%02x%02x" % light)
    img = img.convert("RGB").resize((box_px, box_px), Image.LANCZOS)
    return img


def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def main():
    base = vertical_gradient((W, H), SIDE, INKG)

    # Subtle radial glow behind where the eye will sit
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gcx, gcy, gr = W / 2, H * 0.3, W * 0.42
    gd.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    glow_layer = Image.new("RGB", (W, H), MOSS)
    base = Image.composite(glow_layer, base, glow)

    canvas = base.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Cumulative top-down layout: each block advances `y` by its own
    # measured height plus a gap, so nothing is placed by guesswork.
    y = 55

    # --- Eye/pin logo ---
    logo_size = 230
    logo = make_eye_pin(logo_size)
    canvas.alpha_composite(logo, (int(W / 2 - logo_size / 2), y))
    y += logo_size + 28

    # --- "EE" wordmark ---
    f_wordmark = ImageFont.truetype(LOGO_FONT, 76)
    h = draw_centered_text(draw, (W / 2, y + text_height(draw, "EE", f_wordmark) / 2), "EE", f_wordmark, CREAM)
    y += h + 18

    # --- Kicker / tagline (Arabic) ---
    f_tagline = ImageFont.truetype(ARABIC_FONT, 38)
    tagline = ar("فيه سر مش بيتقال بسهولة")
    h = text_height(draw, tagline, f_tagline)
    draw_centered_text(draw, (W / 2, y + h / 2), tagline, f_tagline, SAGE)
    y += h + 20

    # --- Headline ---
    f_headline = ImageFont.truetype(ARABIC_FONT, 46)
    headline = ar("جرّب تسأله... وشوف هيقولك ايه")
    h = text_height(draw, headline, f_headline)
    draw_centered_text(draw, (W / 2, y + h / 2), headline, f_headline, WHITE)
    y += h + 46

    # --- QR card ---
    qr_box = 270
    card_pad = 26
    f_scan = ImageFont.truetype(ARABIC_FONT, 28)
    scan_text = ar("امسح الكود وابدأ")
    scan_h = text_height(draw, scan_text, f_scan)
    card_w = qr_box + card_pad * 2
    card_h = card_pad + qr_box + 16 + scan_h + card_pad
    card_x = (W - card_w) / 2
    card_y = y
    rounded_rect(
        draw,
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=26,
        fill=CREAM,
    )
    qr_img = make_qr(SITE_URL, qr_box)
    canvas.paste(qr_img, (int(card_x + card_pad), int(card_y + card_pad)))
    draw_centered_text(
        draw,
        (W / 2, card_y + card_pad + qr_box + 16 + scan_h / 2),
        scan_text,
        f_scan,
        INKG,
    )
    y += card_h + 36
    # NOTE: deliberately no plain-text URL fallback here - the real domain
    # (evil-eye-chatbot.vercel.app) spells out the one phrase EE can never
    # say or show, in any language. QR-only avoids printing it anywhere.

    # --- Event teaser pill ---
    pill_text = ar("٩/٩  •  الساعة ٦ مساءً  •  الكنيسة المرقسية")
    f_pill = ImageFont.truetype(ARABIC_FONT, 26)
    bbox = draw.textbbox((0, 0), pill_text, font=f_pill)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pill_pad_x, pill_pad_y = 30, 16
    pill_w, pill_h = tw + pill_pad_x * 2, th + pill_pad_y * 2
    pill_x = (W - pill_w) / 2
    pill_y = y
    rounded_rect(
        draw,
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=pill_h / 2,
        outline=SAGE,
        width=2,
    )
    draw_centered_text(draw, (W / 2, pill_y + pill_h / 2), pill_text, f_pill, SAGE)
    y += pill_h + 20

    print(f"content bottom: {y} / canvas height: {H}")

    out_path = os.path.join(os.path.dirname(__file__), "ee_poster.png")
    canvas.convert("RGB").save(out_path, "PNG")
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
