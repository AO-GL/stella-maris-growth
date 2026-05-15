from __future__ import annotations

import base64
import hashlib
import io
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
import streamlit as st
from openai import OpenAI
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


@dataclass(frozen=True)
class CampaignPreset:
    name: str
    scene: str
    slogan: str
    caption: str
    hashtags: str


PRESETS = [
    CampaignPreset(
        "Geschenk / Unboxing",
        "Eine elegante Frau oeffnet eine hochwertige teal-farbene Geschenkbox mit Stella-Maris-Uhr und Schmuck in einem hellen luxurioesen Schlafzimmer. Rosen, weiche Stoffe, Schmucktablett, warmes Tageslicht.",
        "Ein Geschenk, das bleibt.",
        "Schenke Eleganz, die jeden Tag getragen werden kann.",
        "#StellaMaris #Geschenkidee #SchmuckGeschenk #UhrenLiebe #ZeitloseEleganz",
    ),
    CampaignPreset(
        "Business / Meeting",
        "Eine stilvolle Frau in cremefarbenem Business-Outfit vor einem wichtigen Termin, moderne helle Office- oder Gallery-Atmosphaere, Uhr und Schmuck sichtbar, hochwertig und selbstbewusst.",
        "Stil, der auch ohne Worte ueberzeugt.",
        "Stella Maris begleitet den Moment, in dem aus einem Look ein Auftritt wird.",
        "#StellaMaris #DamenUhr #BusinessStyle #LuxusAccessoires #SchmuckLiebe",
    ),
    CampaignPreset(
        "Abend / Dinner",
        "Eine elegante Frau in einem warm beleuchteten Hotelbar- oder Dinner-Setting, Schmuck, Uhr, Ring und Ohrringe sichtbar, romantische Premium-Atmosphaere.",
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
    CampaignPreset(
        "Hochzeit / Braut",
        "Eine elegante Braut oder Hochzeitsgaestin in heller Seide, Stella-Maris-Uhr und Schmuck sichtbar, weiche Blumen, Spiegel, Champagnerlicht, luxurioese Vorbereitungsszene.",
        "Ein Detail fuer den Tag, der bleibt.",
        "Stella Maris veredelt die Momente, die man nicht wiederholt.",
        "#StellaMaris #WeddingStyle #BrautSchmuck #EleganterLook #ZeitloseEleganz",
    ),
    CampaignPreset(
        "Muttertag / Geschenk",
        "Eine erwachsene Tochter ueberreicht einer eleganten Frau eine hochwertige Schmuckbox, warme Wohnatmosphaere, Uhr und Kette sichtbar, Rosen und persoenlicher Luxusmoment.",
        "Fuer die Frau, die alles bedeutet.",
        "Ein Geschenk mit Stil, Wert und Erinnerung.",
        "#StellaMaris #Muttertag #Geschenkidee #SchmuckGeschenk #UhrenLiebe",
    ),
    CampaignPreset(
        "Cafe / Alltag",
        "Eine stilvolle Frau sitzt in einem hellen eleganten Cafe, Kaffee, Notizbuch, Uhr am Handgelenk, dezenter Schmuck, moderne feminine Alltags-Eleganz.",
        "Alltag, aber mit Haltung.",
        "Kleine Details machen aus einem normalen Tag einen Stella-Maris-Moment.",
        "#StellaMaris #CafeStyle #DamenUhr #SchmuckLiebe #DailyLuxury",
    ),
    CampaignPreset(
        "Beauty / Vanity",
        "Eine elegante Frau vor einem hellen Schminktisch, Parfum, Perlen, Schmucktablett, Uhr und Ohrringe sichtbar, weiche Beauty-Kampagnen-Atmosphaere.",
        "Schoenheit liegt im Detail.",
        "Stella Maris verbindet Schmuck, Uhr und Outfit zu einem ruhigen Luxusmoment.",
        "#StellaMaris #BeautyStyle #JewelleryStyle #LuxusAccessoires #EleganterLook",
    ),
    CampaignPreset(
        "Gala / Event",
        "Eine elegante Frau im Abendkleid auf dem Weg zu einer Gala, dunkler Premium-Hintergrund, warmes Licht, funkelnder Schmuck, Uhr und Ring sichtbar.",
        "Wenn der Moment gross wird.",
        "Ein Auftritt beginnt oft mit dem richtigen Detail.",
        "#StellaMaris #GalaLook #EveningStyle #DiamantSchmuck #StatementLook",
    ),
    CampaignPreset(
        "Sommer / Resort",
        "Eine stilvolle Frau in einem luxurioesen Resort oder auf einer Terrasse am Meer, helles Outfit, Sonnenlicht, Uhr und Schmuck sichtbar, elegante Urlaubsstimmung.",
        "Sommer, der nach Stil aussieht.",
        "Leichte Looks, hochwertige Details und ein Gefuehl von Reise.",
        "#StellaMaris #ResortStyle #TravelStyle #SommerLook #DamenUhr",
    ),
    CampaignPreset(
        "Schmuckdetail / Close-up",
        "Ein hochwertiger Close-up-Moment von Handgelenk, Ring, Kette und Uhr an einer eleganten Frau, weiche Stoffe, Rosen, Perlmutt, Gold- und Teal-Akzente.",
        "Leise Details. Starke Wirkung.",
        "Ein Motiv fuer Produktnaehe, Detailwirkung und hochwertige Social Ads.",
        "#StellaMaris #Schmuckdetail #UhrenLiebe #Perlmutt #Saphirglas",
    ),
    CampaignPreset(
        "Paar / Geschenk Moment",
        "Ein eleganter Partner schenkt einer Frau eine Stella-Maris-Schmuckbox, intime Premium-Atmosphaere, Kerzenlicht, Uhr und Schmuck sichtbar, romantisch aber modern.",
        "Ein Geschenk mit Bedeutung.",
        "Fuer Momente, in denen ein Detail mehr sagt als viele Worte.",
        "#StellaMaris #GeschenkMoment #RomanticGift #SchmuckGeschenk #LuxusAccessoires",
    ),
]


DRAFT_DIRECTIONS = [
    "Variante 1: emotionale Lifestyle-Szene mit Frau, Geschenk, Schmuck und klar sichtbarer Uhr. Sehr hochwertig, warm, nahbar.",
    "Variante 2: eleganter Fashion-Moment mit Outfit, Handgelenk, Schmuckdetails und Premium-Interieur. Mehr Editorial-Look.",
    "Variante 3: produktnaher Luxusmoment mit Handgelenk, Uhr, Ring, Kette, Blumen und hochwertiger Lichtsetzung. Mehr Detailfokus.",
    "Variante 4: helle Beauty-Kampagne mit Schminktisch, Parfum, Seide und Schmucktablett. Sehr feminin und edel.",
    "Variante 5: moderne Business-Szene mit klarer Haltung, hellem Office, Uhr sichtbar und selbstbewusstem Premium-Look.",
    "Variante 6: romantischer Geschenk-Moment mit Box, Rosen, weichen Stoffen und emotionalem Blick auf das Produkt.",
    "Variante 7: luxurioeser Reise- oder Hotelmoment mit Spiegel, Koffer, Seidentuch, Schmuck und Uhr als Stylingdetail.",
    "Variante 8: Abend- und Dinner-Motiv mit warmem Licht, dunkler Eleganz, funkelnden Details und hochwertiger Stimmung.",
    "Variante 9: sehr naher Detail-Shot von Schmuck, Uhr, Handgelenk, Ring und hochwertiger Materialwirkung.",
    "Variante 10: freier Social-Ad-Moment mit unerwarteter, aber realistischer Stella-Maris-Luxuskomposition.",
]


LOCAL_SLOGAN_POOL = [
    "Ein Detail, das deinen Look vollendet.",
    "Eleganz, die jeden Moment begleitet.",
    "Kleine Details. Grosser Auftritt.",
    "Zeitlos schoen. Jeden Tag tragbar.",
    "Stil beginnt am Handgelenk.",
    "Luxus, der leise wirkt.",
    "Fuer Momente, die bleiben.",
    "Mehr als Schmuck. Ein Gefuehl.",
    "Dein Look. Dein Moment. Stella Maris.",
    "Wenn Details den Unterschied machen.",
    "Feine Eleganz fuer starke Auftritte.",
    "Schoenheit, die nicht laut sein muss.",
    "Ein Geschenk mit Bedeutung.",
    "Der letzte Schliff fuer deinen Stil.",
    "Premium-Details fuer jeden Tag.",
]


def get_api_key() -> str | None:
    try:
        return st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    except Exception:
        return os.getenv("OPENAI_API_KEY")


def stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def clean_slogan_line(line: str) -> str:
    line = re.sub(r"^\s*[-*]?\s*\d*[\).:-]?\s*", "", line).strip()
    line = line.strip('"').strip("'").strip()
    return line


def fallback_slogans(preset: CampaignPreset, round_index: int = 0) -> list[str]:
    rotated = LOCAL_SLOGAN_POOL[round_index % len(LOCAL_SLOGAN_POOL) :] + LOCAL_SLOGAN_POOL[: round_index % len(LOCAL_SLOGAN_POOL)]
    options = [preset.slogan] + rotated
    unique: list[str] = []
    for option in options:
        if option and option not in unique:
            unique.append(option)
    return unique[:5]


def parse_slogans(text: str) -> list[str]:
    slogans: list[str] = []
    for line in text.replace("\r", "\n").split("\n"):
        slogan = clean_slogan_line(line)
        if 8 <= len(slogan) <= 70 and slogan not in slogans:
            slogans.append(slogan)
    return slogans[:5]


def generate_slogans(api_key: str | None, preset: CampaignPreset, extra_brief: str, round_index: int) -> list[str]:
    fallback = fallback_slogans(preset, round_index)
    if not api_key:
        return fallback

    prompt = f"""
Erstelle exakt 5 kurze deutsche Premium-Slogans fuer Stella Maris Uhren und Schmuck.
Motiv: {preset.name}
Szene: {preset.scene}
Zusatzwunsch: {extra_brief or "edler, femininer Luxus fuer Social Media"}
Regeln:
- Jede Zeile genau ein Slogan.
- Maximal 8 Woerter pro Slogan.
- Hochwertig, elegant, emotional, nicht kitschig.
- Keine Hashtags, keine Emojis, keine Anfuehrungszeichen.
- Keine Erklaerungen.
Runde: {round_index}
""".strip()

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini"),
            input=prompt,
        )
        slogans = parse_slogans(getattr(response, "output_text", ""))
        return slogans if len(slogans) == 5 else fallback
    except Exception:
        return fallback


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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


def image_prompt(scene: str, extra_brief: str, draft_direction: str, change_request: str = "") -> str:
    change_block = (
        f"Required revision from user: {change_request}. Keep the Stella Maris premium luxury direction."
        if change_request
        else "No revision requested yet."
    )
    return f"""
Use case: ads-marketing
Asset type: Instagram luxury campaign image, portrait 4:5
Primary request: Create a photorealistic premium lifestyle campaign image for Stella Maris watches and jewelry.
Scene: {scene}
Draft direction: {draft_direction}
Additional user direction: {extra_brief or "keep it elegant, premium, feminine, refined, and realistic"}
{change_block}
Subject: stylish woman aged around 30-40 wearing a premium white, silver or rose-gold watch, delicate necklace, earrings or ring. Jewelry and watch should be visible naturally.
Style: high-end editorial fashion advertising photography, realistic, elegant, aspirational, refined, not cheap stock-photo.
Composition: vertical 4:5 social ad image, clear woman in a fitting situation, product visible, space in lower third for a slogan.
Lighting: soft luxury daylight or warm premium evening light, depending on the scene.
Palette: ivory, champagne gold, deep teal, soft rose, pearl white.
Text: no text, no logo, no watermark in the generated image. The app will add text later.
Avoid: distorted hands, extra fingers, unrealistic jewelry, third-party logos, messy background, flat product cutout, transparent overlay boxes, cartoon look.
""".strip()


def generate_campaign_image(
    api_key: str,
    scene: str,
    extra_brief: str,
    quality: str,
    draft_direction: str,
    change_request: str = "",
) -> Image.Image:
    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt(scene, extra_brief, draft_direction, change_request),
        size="1024x1536",
        quality=quality,
    )
    image_base64 = result.data[0].b64_json
    image_bytes_data = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(image_bytes_data)).convert("RGB")


def image_upload_file(image: Image.Image) -> io.BytesIO:
    image_file = io.BytesIO()
    image.save(image_file, format="PNG")
    image_file.seek(0)
    image_file.name = "stella-maris-source.png"
    return image_file


def edit_prompt(scene: str, extra_brief: str, draft_direction: str, change_request: str) -> str:
    return f"""
Edit this Stella Maris luxury campaign image according to the user's revision.
Revision: {change_request}
Original scene direction: {scene}
Draft direction: {draft_direction}
Additional brand direction: {extra_brief or "premium, elegant, feminine, realistic"}
Keep: high-end editorial lifestyle photography, realistic woman, visible watch and jewelry, premium Stella Maris mood, clean space for later slogan text.
Do not add text, logos, watermarks or transparent boxes. Keep hands and jewelry realistic.
""".strip()


def edit_campaign_image(
    api_key: str,
    source: Image.Image,
    scene: str,
    extra_brief: str,
    quality: str,
    draft_direction: str,
    change_request: str,
) -> Image.Image:
    client = OpenAI(api_key=api_key)
    result = client.images.edit(
        model="gpt-image-1",
        image=image_upload_file(source),
        prompt=edit_prompt(scene, extra_brief, draft_direction, change_request),
        size="1024x1536",
        quality=quality,
    )
    image_base64 = result.data[0].b64_json
    image_bytes_data = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(image_bytes_data)).convert("RGB")


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font_obj: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    shadow: tuple[int, int, int, int] = (0, 0, 0, 150),
) -> None:
    x, y = position
    draw.text((x + 3, y + 3), text, fill=shadow, font=font_obj)
    draw.text((x, y), text, fill=fill, font=font_obj)


def render_poster(source: Image.Image, slogan: str, cta: str) -> Image.Image:
    poster = source.resize((1080, 1350), Image.Resampling.LANCZOS)
    poster = ImageEnhance.Color(poster).enhance(1.04)
    poster = ImageEnhance.Contrast(poster).enhance(1.03)

    overlay = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fade = Image.new("RGBA", poster.size, (0, 0, 0, 0))
    fade_draw = ImageDraw.Draw(fade)
    for y in range(780, 1350):
        alpha = int(118 * ((y - 780) / 570))
        fade_draw.line([(0, y), (1080, y)], fill=(5, 38, 40, alpha))
    overlay.alpha_composite(fade)

    brand_font = font(52, bold=True)
    slogan_font = font(74, bold=True)
    cta_font = font(34, bold=True)

    draw_text_with_shadow(draw, (64, 76), "STELLA MARIS", brand_font, (255, 255, 255, 248))

    y = 914
    for line in wrap(draw, slogan, slogan_font, 920)[:3]:
        draw_text_with_shadow(draw, (64, y), line, slogan_font, (255, 255, 255, 255))
        y += 84

    draw_text_with_shadow(draw, (64, 1242), cta.upper(), cta_font, (248, 228, 182, 255), (0, 0, 0, 120))
    return Image.alpha_composite(poster.convert("RGBA"), overlay).convert("RGB")


def image_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt, optimize=True)
    return buf.getvalue()


def cover_crop(image: Image.Image, size: tuple[int, int], zoom: float, pan_x: float, pan_y: float) -> Image.Image:
    target_w, target_h = size
    source = image.convert("RGB")
    scale = max(target_w / source.width, target_h / source.height) * zoom
    resized = source.resize((int(source.width * scale), int(source.height * scale)), Image.Resampling.LANCZOS)
    max_left = max(0, resized.width - target_w)
    max_top = max(0, resized.height - target_h)
    left = int(max_left * min(max(pan_x, 0.0), 1.0))
    top = int(max_top * min(max(pan_y, 0.0), 1.0))
    return resized.crop((left, top, left + target_w, top + target_h))


def ease(value: float) -> float:
    return value * value * (3 - 2 * value)


def add_video_copy(frame: Image.Image, headline: str, subline: str, brand: str = "STELLA MARIS") -> Image.Image:
    frame = frame.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    fade = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    fade_draw = ImageDraw.Draw(fade)
    for y in range(760, 1280):
        alpha = int(150 * ((y - 760) / 520))
        fade_draw.line([(0, y), (720, y)], fill=(5, 35, 37, alpha))
    overlay.alpha_composite(fade)

    brand_font = font(33, bold=True)
    headline_font = font(52, bold=True)
    subline_font = font(24, bold=True)

    draw_text_with_shadow(draw, (42, 54), brand, brand_font, (255, 255, 255, 245))

    y = 925
    for line in wrap(draw, headline, headline_font, 620)[:3]:
        draw_text_with_shadow(draw, (42, y), line, headline_font, (255, 255, 255, 255))
        y += 61

    draw_text_with_shadow(draw, (42, 1190), subline.upper(), subline_font, (248, 228, 182, 255))
    return Image.alpha_composite(frame, overlay).convert("RGB")


def render_reel_mp4(posters: list[Image.Image], slogan: str, video_brief: str, cta: str) -> bytes:
    fps = 10
    duration_seconds = 20
    frame_count = fps * duration_seconds
    size = (720, 1280)
    parts = [part.strip() for part in video_brief.split(",") if part.strip()]
    subtitles = (parts + ["Schmuckdetail", "Premium-Look", "Jetzt speichern"])[:4]
    headlines = [
        slogan,
        "Details, die leise wirken.",
        "Luxus fuer deinen Moment.",
        cta,
    ]

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        writer = imageio.get_writer(
            str(tmp_path),
            fps=fps,
            codec="libx264",
            quality=7,
            macro_block_size=16,
            output_params=["-pix_fmt", "yuv420p"],
        )

        for frame_number in range(frame_count):
            seconds = frame_number / fps
            scene_index = min(3, int(seconds // 5))
            local = (seconds - scene_index * 5) / 5
            smooth = ease(local)
            poster = posters[scene_index % len(posters)]
            zoom = 1.02 + smooth * 0.10
            pan_x = [0.48, 0.58, 0.42, 0.50][scene_index] + (smooth - 0.5) * 0.12
            pan_y = [0.42, 0.46, 0.52, 0.50][scene_index] + (smooth - 0.5) * 0.08
            frame = cover_crop(poster, size, zoom, pan_x, pan_y)
            frame = ImageEnhance.Contrast(frame).enhance(1.03)
            frame = ImageEnhance.Color(frame).enhance(1.04)

            if local < 0.10:
                fade_alpha = int((1 - local / 0.10) * 120)
                frame = Image.blend(Image.new("RGB", size, (5, 35, 37)), frame, 1 - fade_alpha / 255)

            frame = add_video_copy(frame, headlines[scene_index], subtitles[scene_index])
            writer.append_data(np.asarray(frame))

        writer.close()
        return tmp_path.read_bytes()
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


def create_draft(
    api_key: str,
    preset: CampaignPreset,
    extra_brief: str,
    slogan: str,
    cta: str,
    quality: str,
    draft_direction: str,
    change_request: str = "",
    source_image: Image.Image | None = None,
) -> dict:
    if source_image is not None and change_request:
        try:
            image = edit_campaign_image(
                api_key,
                source_image,
                preset.scene,
                extra_brief,
                quality,
                draft_direction,
                change_request,
            )
        except Exception:
            image = generate_campaign_image(api_key, preset.scene, extra_brief, quality, draft_direction, change_request)
    else:
        image = generate_campaign_image(api_key, preset.scene, extra_brief, quality, draft_direction, change_request)
    return {
        "id": str(uuid.uuid4()),
        "direction": draft_direction,
        "source": image,
        "poster": render_poster(image, slogan, cta),
        "change_note": change_request,
    }


def selected_preset(name: str) -> CampaignPreset:
    return next(item for item in PRESETS if item.name == name)


st.set_page_config(page_title="Stella Maris Content Autopilot", layout="wide")
st.title("Stella Maris Content Autopilot")
st.caption(
    "Erzeugt pro Kampagne 0 bis 10 Premium-Bildentwuerfe, direkte Sloganbilder und ein ca. 20 Sekunden langes MP4-Reel."
)

api_key = get_api_key()
if not api_key:
    st.warning("OPENAI_API_KEY fehlt. Lege ihn in Streamlit Cloud unter App > Settings > Secrets an.")
    st.code('OPENAI_API_KEY = "dein_api_key"', language="toml")

if "campaigns" not in st.session_state:
    st.session_state.campaigns = []
if "slogan_options" not in st.session_state:
    st.session_state.slogan_options = []
if "slogan_context" not in st.session_state:
    st.session_state.slogan_context = ""
if "slogan_round" not in st.session_state:
    st.session_state.slogan_round = 0

with st.sidebar:
    st.header("Kampagne erzeugen")
    preset_name = st.selectbox("Motiv", [preset.name for preset in PRESETS])
    preset = selected_preset(preset_name)
    extra_brief = st.text_area(
        "Eigene Bildbeschreibung",
        placeholder="z.B. Frau mit Geschenkbox, Rosen, helle Luxusatmosphaere, weisses Outfit",
    )
    slogan_context = f"{preset.name}|{extra_brief}"
    if st.session_state.slogan_context != slogan_context:
        st.session_state.slogan_context = slogan_context
        st.session_state.slogan_round = 0
        st.session_state.slogan_options = fallback_slogans(preset, st.session_state.slogan_round)

    st.markdown("**Slogan-Entwuerfe**")
    if st.button("Neue 5 Slogans erstellen"):
        st.session_state.slogan_round += 1
        with st.spinner("Erstelle 5 neue Slogans..."):
            st.session_state.slogan_options = generate_slogans(
                api_key,
                preset,
                extra_brief,
                st.session_state.slogan_round,
            )

    if not st.session_state.slogan_options:
        st.session_state.slogan_options = fallback_slogans(preset, st.session_state.slogan_round)

    slogan_choice_key = f"slogan_choice_{stable_hash(st.session_state.slogan_context + str(st.session_state.slogan_round))}"
    selected_slogan = st.selectbox(
        "Slogan auswaehlen",
        st.session_state.slogan_options,
        key=slogan_choice_key,
    )
    slogan_edit_key = f"slogan_edit_{stable_hash(selected_slogan + str(st.session_state.slogan_round))}"
    slogan = st.text_input("Slogan im Bild bearbeiten", value=selected_slogan, key=slogan_edit_key)
    cta = st.text_input("CTA im Bild", value="Inspiration speichern")
    quality = st.selectbox("Qualitaet", ["medium", "high", "low"], index=0)
    video_brief = st.text_input("Video-Szenen", value="Lifestyle-Moment, Schmuckdetail, Outfit, CTA")
    draft_count = st.selectbox("Anzahl Entwuerfe", list(range(0, 11)), index=3)
    generate = st.button(f"{draft_count} Entwuerfe erzeugen", disabled=not api_key)

if generate and api_key and draft_count == 0:
    st.info("0 Entwuerfe gewaehlt. Es wurde nichts erzeugt.")

if generate and api_key and draft_count > 0:
    progress = st.progress(0, text=f"Erzeuge {draft_count} unterschiedliche Bildentwuerfe...")
    drafts = []
    try:
        for index, direction in enumerate(DRAFT_DIRECTIONS[:draft_count], start=1):
            drafts.append(create_draft(api_key, preset, extra_brief, slogan, cta, quality, direction))
            progress.progress(int(index / draft_count * 100), text=f"Entwurf {index} von {draft_count} fertig")
        st.session_state.campaigns.insert(
            0,
            {
                "id": str(uuid.uuid4()),
                "preset_name": preset.name,
                "extra_brief": extra_brief,
                "slogan": slogan,
                "cta": cta,
                "quality": quality,
                "video_brief": video_brief,
                "caption": preset.caption,
                "hashtags": preset.hashtags,
                "drafts": drafts,
                "video": None,
            },
        )
        progress.empty()
        st.success(f"{draft_count} unterschiedliche Entwuerfe erzeugt. Du kannst jeden Entwurf unten aendern lassen.")
    except Exception as exc:
        progress.empty()
        st.error(f"Die Generierung ist fehlgeschlagen: {exc}")

if not st.session_state.campaigns:
    st.info(
        "Waehle links ein Motiv, die Anzahl der Entwuerfe und klicke auf 'Entwuerfe erzeugen'. Die App erzeugt neue Bilder per KI, keine festen Asset-Dateien."
    )

for campaign in st.session_state.campaigns:
    preset = selected_preset(campaign["preset_name"])
    st.divider()
    st.subheader(campaign["preset_name"])
    st.write(campaign["caption"])
    st.code(campaign["hashtags"], language=None)

    for row_start in range(0, len(campaign["drafts"]), 3):
        row_drafts = campaign["drafts"][row_start : row_start + 3]
        columns = st.columns(len(row_drafts))
        for offset, draft in enumerate(row_drafts):
            draft_index = row_start + offset
            with columns[offset]:
                st.image(draft["poster"], use_container_width=True)
                st.download_button(
                    "Bild herunterladen",
                    image_bytes(draft["poster"]),
                    file_name=f"stella-maris-{campaign['id'][:8]}-entwurf-{draft_index + 1}.png",
                    mime="image/png",
                    key=f"download_image_{draft['id']}",
                )
                with st.form(f"edit_form_{draft['id']}"):
                    change_request = st.text_area(
                        "Aenderungen fuer dieses Bild",
                        value="",
                        placeholder="z.B. mehr Schmuck sichtbar, anderes Outfit, mehr Hotelzimmer, weniger Textflaeche",
                        key=f"change_text_{draft['id']}",
                    )
                    submitted = st.form_submit_button("Entwurf neu erzeugen")
                if submitted:
                    if not api_key:
                        st.error("OPENAI_API_KEY fehlt.")
                    elif not change_request.strip():
                        st.warning("Bitte beschreibe kurz, was geaendert werden soll.")
                    else:
                        with st.spinner("Erzeuge geaenderte Bildvariante..."):
                            try:
                                campaign["drafts"][draft_index] = create_draft(
                                    api_key,
                                    preset,
                                    campaign["extra_brief"],
                                    campaign["slogan"],
                                    campaign["cta"],
                                    campaign["quality"],
                                    draft["direction"],
                                    change_request.strip(),
                                    source_image=draft["source"],
                                )
                                campaign["video"] = None
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Aenderung fehlgeschlagen: {exc}")

    video_col, copy_col = st.columns([1, 1])
    with video_col:
        draft_total = len(campaign["drafts"])
        if st.button(
            f"20-Sekunden-Video aus {draft_total} Entwuerfen erstellen",
            key=f"video_button_{campaign['id']}",
            disabled=draft_total == 0,
        ):
            with st.spinner("Erstelle MP4-Video mit mehreren Szenen..."):
                try:
                    campaign["video"] = render_reel_mp4(
                        [draft["poster"] for draft in campaign["drafts"]],
                        campaign["slogan"],
                        campaign["video_brief"],
                        campaign["cta"],
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Video konnte nicht erstellt werden: {exc}")
        if campaign.get("video"):
            st.video(campaign["video"])
            st.download_button(
                "Video herunterladen",
                campaign["video"],
                file_name=f"stella-maris-{campaign['id'][:8]}-reel-20s.mp4",
                mime="video/mp4",
                key=f"download_video_{campaign['id']}",
            )

    with copy_col:
        st.markdown("**Slogan**")
        st.write(campaign["slogan"])
        st.markdown("**Caption**")
        st.write(campaign["caption"])
        st.markdown("**Video-Szenen**")
        st.write(campaign["video_brief"])
