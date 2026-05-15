from __future__ import annotations

import base64
import io
import os
from dataclasses import dataclass

import streamlit as st
from openai import OpenAI
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


@dataclass
class CampaignPreset:
    name: str
    scene: str
    slogan: str
    caption: str
    hashtags: str


PRESETS = [
    CampaignPreset(
        "Geschenk / Unboxing",
        "Eine elegante Frau oeffnet eine hochwertige teal-farbene Geschenkbox mit Uhr und Schmuck in einem hellen, luxuriösen Schlafzimmer. Rosen, weiche Stoffe, Schmucktablett, warmes Tageslicht.",
        "Ein Geschenk, das bleibt.",
        "Schenke Eleganz, die jeden Tag getragen werden kann.",
        "#StellaMaris #Geschenkidee #SchmuckGeschenk #UhrenLiebe #ZeitloseEleganz",
    ),
    CampaignPreset(
        "Business / Meeting",
        "Eine stilvolle Frau in cremefarbenem Business-Outfit vor einem wichtigen Termin, moderne helle Office-/Gallery-Atmosphäre, Uhr und Schmuck sichtbar, hochwertig und selbstbewusst.",
        "Stil, der auch ohne Worte ueberzeugt.",
        "Stella Maris begleitet den Moment, in dem aus einem Look ein Auftritt wird.",
        "#StellaMaris #DamenUhr #BusinessStyle #LuxusAccessoires #SchmuckLiebe",
    ),
    CampaignPreset(
        "Abend / Dinner",
        "Eine elegante Frau in einem warm beleuchteten Hotelbar- oder Dinner-Setting, Schmuck, Uhr, Ring und Ohrringe sichtbar, romantische Premium-Atmosphäre.",
        "Wenn der Abend glaenzt, beginnt dein Auftritt.",
        "Ein elegantes Detail, das Dinner, Event und besondere Momente veredelt.",
        "#StellaMaris #EveningLook #DiamantSchmuck #EleganterLook #JewelleryStyle",
    ),
    CampaignPreset(
        "Reise / Hotel",
        "Eine stilvolle Frau in einem Boutique-Hotelzimmer, sie richtet ein Seidentuch oder Schmuck vor dem Spiegel, Reiseaccessoires, Blumen und Uhr sichtbar.",
        "Bereit fuer jeden besonderen Moment.",
        "Uhr und Schmuck als stilvolle Begleiter fuer Reise, Alltag und besondere Plaene.",
        "#StellaMaris #TravelStyle #DamenUhr #OutfitInspiration #AccessoireLiebe",
    ),
]


def get_api_key() -> str | None:
    try:
        return st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        width = draw.textbbox((0, 0), trial, font=font_obj)[2]
        if width > max_width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def image_prompt(scene: str, extra_brief: str) -> str:
    return f"""
Use case: ads-marketing
Asset type: Instagram luxury campaign image, portrait 4:5
Primary request: Create a photorealistic premium lifestyle campaign image for Stella Maris watches and jewelry.
Scene: {scene}
Additional user direction: {extra_brief or "keep it elegant, premium, feminine, refined, and realistic"}
Subject: stylish woman aged around 30-40 wearing a premium white or rose-gold watch, delicate necklace, earrings or ring. Jewelry and watch should be visible naturally.
Style: high-end editorial fashion advertising photography, realistic, elegant, aspirational.
Composition: vertical 4:5 social ad image, clear subject, product visible, enough clean space for a slogan overlay.
Lighting: soft luxury daylight or warm premium evening light, depending on the scene.
Palette: ivory, champagne gold, deep teal, soft rose, pearl white.
Text: no text in the generated image. The app will add text later.
Avoid: watermark, distorted hands, extra fingers, unrealistic jewelry, third-party logos, messy background, cheap stock-photo look.
""".strip()


def generate_campaign_image(api_key: str, scene: str, extra_brief: str, quality: str) -> Image.Image:
    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt(scene, extra_brief),
        size="1024x1536",
        quality=quality,
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def render_poster(source: Image.Image, slogan: str, cta: str) -> Image.Image:
    poster = source.resize((1080, 1350), Image.Resampling.LANCZOS)
    poster = ImageEnhance.Color(poster).enhance(1.04)
    poster = ImageEnhance.Contrast(poster).enhance(1.03)

    overlay = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fade = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    fade_draw = ImageDraw.Draw(fade)
    for y in range(790, 1350):
        alpha = int(125 * ((y - 790) / 560))
        fade_draw.line([(0, y), (1080, y)], fill=(5, 38, 40, alpha))
    overlay.alpha_composite(fade)

    brand_font = font(52, bold=True)
    slogan_font = font(76, bold=True)
    cta_font = font(34, bold=True)

    draw.text((64, 74), "STELLA MARIS", fill=(255, 255, 255, 245), font=brand_font)

    y = 920
    for line in wrap(draw, slogan, slogan_font, 930)[:3]:
        draw.text((64, y), line, fill=(255, 255, 255, 255), font=slogan_font)
        y += 84

    draw.text((64, 1245), cta.upper(), fill=(248, 228, 182, 255), font=cta_font)
    return Image.alpha_composite(poster.convert("RGBA"), overlay).convert("RGB")


def image_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt, optimize=True)
    return buf.getvalue()


def render_reel_gif(poster: Image.Image, video_brief: str, cta: str) -> bytes:
    base = poster.resize((540, 675), Image.Resampling.LANCZOS)
    captions = [part.strip() for part in video_brief.split(",")[:3] if part.strip()]
    captions = captions or ["Lifestyle-Moment", "Detail & Eleganz", cta]
    frames = []

    for i in range(45):
        phase = min(2, i // 15)
        zoom = 1.0 + (i % 15) * 0.006
        w, h = base.size
        crop_w, crop_h = int(w / zoom), int(h / zoom)
        left = (w - crop_w) // 2
        top = (h - crop_h) // 2
        frame = base.crop((left, top, left + crop_w, top + crop_h)).resize((540, 675), Image.Resampling.LANCZOS)
        frame = frame.convert("RGBA")
        draw = ImageDraw.Draw(frame)
        draw.text((32, 584), captions[min(phase, len(captions) - 1)], fill=(248, 228, 182, 255), font=font(26, bold=True))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))

    buf = io.BytesIO()
    frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=90, loop=0)
    return buf.getvalue()


st.set_page_config(page_title="Stella Maris Content Autopilot", layout="wide")
st.title("Stella Maris Content Autopilot")
st.caption("Erzeugt neue, hochwertige Marketingbilder im Stella-Maris-Stil und schreibt den Slogan direkt ins Bild.")

api_key = get_api_key()
if not api_key:
    st.warning("OPENAI_API_KEY fehlt. Lege ihn in Streamlit Cloud unter App > Settings > Secrets an.")
    st.code('OPENAI_API_KEY = "dein_api_key"', language="toml")

with st.sidebar:
    st.header("Bild generieren")
    preset_name = st.selectbox("Motiv", [preset.name for preset in PRESETS])
    preset = next(item for item in PRESETS if item.name == preset_name)
    extra_brief = st.text_area("Eigene Bildbeschreibung", placeholder="z.B. Frau mit Geschenkbox, Rosen, helle Luxusatmosphaere")
    slogan = st.text_input("Slogan", value=preset.slogan)
    cta = st.text_input("CTA", value="Inspiration speichern")
    quality = st.selectbox("Qualitaet", ["medium", "high", "low"], index=0)
    video_brief = st.text_input("Video-Beschreibung", value="Lifestyle-Moment, Schmuckdetail, CTA")
    generate = st.button("Neues Marketingbild erzeugen", disabled=not api_key)

if "generated" not in st.session_state:
    st.session_state.generated = []

if generate and api_key:
    with st.spinner("Erzeuge neues Marketingbild..."):
        image = generate_campaign_image(api_key, preset.scene, extra_brief, quality)
        poster = render_poster(image, slogan, cta)
        st.session_state.generated.insert(
            0,
            {
                "preset": preset,
                "source": image,
                "poster": poster,
                "slogan": slogan,
                "cta": cta,
                "video_brief": video_brief,
            },
        )

if not st.session_state.generated:
    st.info("Waehle links ein Motiv und klicke auf 'Neues Marketingbild erzeugen'. Die App erzeugt dann ein neues Bild, keine fest hinterlegte Asset-Datei.")

for index, item in enumerate(st.session_state.generated):
    preset = item["preset"]
    poster = item["poster"]
    gif = render_reel_gif(poster, item["video_brief"], item["cta"])

    st.subheader(preset.name)
    st.image(poster, use_container_width=True)
    st.markdown(f"**Slogan:** {item['slogan']}")
    st.write(preset.caption)
    st.code(preset.hashtags, language=None)
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Bild herunterladen",
            image_bytes(poster),
            file_name=f"stella-maris-marketingbild-{index + 1}.png",
            mime="image/png",
        )
    with right:
        st.download_button(
            "Animiertes Reel herunterladen",
            gif,
            file_name=f"stella-maris-reel-{index + 1}.gif",
            mime="image/gif",
        )
