import base64
import random
from datetime import datetime, time
from io import BytesIO
from urllib.parse import urljoin, urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageOps

st.set_page_config(
    page_title="Stella Maris AI Marketing Studio",
    page_icon="💎",
    layout="wide",
)

STELLA_URLS = [
    "https://www.stella-maris-world.com",
    "https://www.stella-maris-world.de",
]

SAFE_WINDOWS = [
    ("Morgen", time(8, 0), time(10, 0)),
    ("Mittag", time(12, 0), time(14, 0)),
    ("Abend", time(17, 30), time(20, 30)),
]

DEFAULT_TAGS = "#stellamaris #uhrenliebe #schmuckliebe #damenuhr #luxurywatch #premiumstyle #geschenkidee"

SLOGANS = [
    "Zeitlose Eleganz für besondere Momente.",
    "Luxus beginnt bei den Details.",
    "Ein Statement aus Stil, Glanz und Präzision.",
    "Eleganz, die jeden Look veredelt.",
    "Stella Maris – gemacht für unvergessliche Augenblicke.",
]

SYSTEM_NOTE = """
Diese App erstellt echte AI-Marketingbilder nur, wenn ein OpenAI API Key eingetragen ist.
Ohne API Key zeigt sie Produktbilder, Texte, Prompts, Captions und Storyboards.
"""


def is_safe_time(selected_time):
    return any(start <= selected_time <= end for _, start, end in SAFE_WINDOWS)


def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def clean_text(text, max_len=600):
    text = " ".join((text or "").split())
    return text[:max_len]


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_page_assets(url):
    headers = {
        "User-Agent": "Mozilla/5.0 StellaMarisMarketingStudio/1.0"
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    texts = []
    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        t = clean_text(tag.get_text(" ", strip=True), 220)
        if len(t) > 25 and t not in texts:
            texts.append(t)

    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src:
            continue

        full = urljoin(url, src)
        alt = clean_text(img.get("alt", ""), 120)

        lower = full.lower()
        if not any(ext in lower for ext in [".jpg", ".jpeg", ".webp", ".png"]):
            continue

        if full not in [x["url"] for x in images]:
            images.append({"url": full, "alt": alt})

    return {
        "url": url,
        "texts": texts[:25],
        "images": images[:30],
    }


@st.cache_data(show_spinner=False, ttl=3600)
def download_image_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 StellaMarisMarketingStudio/1.0"}
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")
    return img


def make_prompt(product_focus, source_text, slogan, image_note):
    return f"""
Create a high-end square luxury marketing image for the watch and jewelry brand Stella Maris.

Scene:
An elegant woman model wearing or presenting the Stella Maris product.
The mood should look like a premium jewelry/watch campaign: bright luxury interior, cream and champagne colors, elegant flowers, soft daylight, realistic skin, premium styling, editorial fashion photography.

Product:
{product_focus}

Use this source text as brand/product inspiration:
{source_text}

Slogan to integrate cleanly into the final campaign visual:
{slogan}

Product image reference:
{image_note}

Important:
- make it photorealistic
- luxury watch and jewelry marketing style
- elegant woman model
- product should be visible and naturally worn or presented
- clean space for short slogan
- no fake brand names except Stella Maris
- premium Instagram campaign image
- square composition
"""


def generate_ai_image(api_key, prompt):
    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="high",
        n=1,
    )

    b64 = result.data[0].b64_json
    raw = base64.b64decode(b64)
    img = Image.open(BytesIO(raw)).convert("RGB")
    return img


def convert_to_2000_jpg(img, slogan=None):
    img = ImageOps.fit(img, (2000, 2000), method=Image.Resampling.LANCZOS)

    if slogan:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = get_font(74)
        small = get_font(38)

        # translucent lower panel
        draw.rectangle((0, 1640, 2000, 2000), fill=(0, 0, 0, 95))
        draw.text((110, 1705), "STELLA MARIS", fill=(235, 210, 150, 255), font=small)
        draw.text((110, 1770), slogan, fill=(255, 255, 255, 255), font=font)

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    out = BytesIO()
    img.save(out, format="JPEG", quality=95, dpi=(300, 300))
    out.seek(0)
    return out


def make_preview_card(product_img, slogan):
    base = Image.new("RGB", (2000, 2000), (246, 242, 235))
    draw = ImageDraw.Draw(base)
    gold = (184, 145, 60)
    dark = (30, 30, 32)

    draw.rectangle((90, 90, 1910, 1910), outline=gold, width=10)
    draw.text((150, 145), "STELLA MARIS", fill=dark, font=get_font(100))
    draw.line((150, 280, 720, 280), fill=gold, width=8)

    product = product_img.copy().convert("RGB")
    product.thumbnail((1200, 1050), Image.Resampling.LANCZOS)
    x = (2000 - product.width) // 2
    y = 430
    base.paste(product, (x, y))

    draw.text((150, 1550), slogan, fill=dark, font=get_font(72))
    draw.text((150, 1660), "Luxury Collection · Social Media Ready", fill=gold, font=get_font(42))

    out = BytesIO()
    base.save(out, format="JPEG", quality=95, dpi=(300, 300))
    out.seek(0)
    return out


st.title("💎 Stella Maris AI Marketing Studio")
st.caption("Holt Produktbilder/Texte von Stella-Maris-Webseiten oder eigenen Links und erstellt daraus hochwertige Marketingbilder.")

st.info(SYSTEM_NOTE)

with st.sidebar:
    st.header("Einstellungen")
    api_key = st.text_input("OpenAI API Key für echte AI-Bilder", type="password")
    amount = st.number_input("Wie viele Entwürfe?", min_value=1, max_value=10, value=3, step=1)
    product_focus = st.selectbox(
        "Produkt-Fokus",
        ["Damenuhr", "Schmuck", "Uhren & Schmuck Set", "Keramikuhr", "Diamantschmuck", "Geschenkidee"],
    )
    posting_time = st.time_input("Geplante Posting-Zeit", value=datetime.now().time().replace(second=0, microsecond=0))

    if is_safe_time(posting_time):
        st.success("Sicheres Posting-Zeitfenster")
    else:
        st.warning("Besser: 08–10, 12–14 oder 17:30–20:30")

tab1, tab2, tab3 = st.tabs(["1. Quellen", "2. Entwürfe generieren", "3. Hinweise"])

with tab1:
    st.subheader("Bild- und Textquelle auswählen")

    source_mode = st.radio(
        "Quelle",
        ["Stella Maris Webseiten", "Eigene Produktbilder", "Eigener Produktlink"],
        horizontal=True,
    )

    selected_images = []
    source_texts = []

    if source_mode == "Stella Maris Webseiten":
        cols = st.columns(2)
        assets_all = []
        for u in STELLA_URLS:
            with st.spinner(f"Lade {u} ..."):
                try:
                    assets = fetch_page_assets(u)
                    assets_all.append(assets)
                    source_texts.extend(assets["texts"])
                except Exception as e:
                    st.error(f"Konnte {u} nicht laden: {e}")

        image_candidates = []
        for assets in assets_all:
            image_candidates.extend(assets["images"])

        st.write(f"Gefundene Bildquellen: {len(image_candidates)}")
        st.write(f"Gefundene Textbausteine: {len(source_texts)}")

        if image_candidates:
            options = [f"{i+1}. {x['alt'] or x['url'][:80]}" for i, x in enumerate(image_candidates)]
            chosen = st.multiselect("Produktbilder von Webseite auswählen", options, default=options[:min(3, len(options))])
            chosen_indexes = [options.index(x) for x in chosen]

            preview_cols = st.columns(3)
            for p, idx in enumerate(chosen_indexes[:9]):
                item = image_candidates[idx]
                try:
                    img = download_image_from_url(item["url"])
                    selected_images.append(img)
                    with preview_cols[p % 3]:
                        st.image(img, caption=item["alt"] or "Produktbild", width=180)
                except Exception as e:
                    st.warning(f"Bild konnte nicht geladen werden: {item['url']}")

    elif source_mode == "Eigene Produktbilder":
        uploaded = st.file_uploader(
            "JPG/JPEG Produktbilder hochladen",
            type=["jpg", "jpeg"],
            accept_multiple_files=True,
        )
        if uploaded:
            for f in uploaded:
                selected_images.append(Image.open(f).convert("RGB"))
            cols = st.columns(3)
            for i, img in enumerate(selected_images):
                with cols[i % 3]:
                    st.image(img, width=180)

        source_texts.append("Stella Maris steht für elegante Uhren und Schmuck mit Premium-Look.")

    else:
        url = st.text_input("Produkt-/Webseiten-Link eingeben")
        if url:
            try:
                assets = fetch_page_assets(url)
                source_texts.extend(assets["texts"])
                st.success(f"Quelle geladen: {url}")
                image_candidates = assets["images"]

                options = [f"{i+1}. {x['alt'] or x['url'][:80]}" for i, x in enumerate(image_candidates)]
                chosen = st.multiselect("Bilder aus Link auswählen", options, default=options[:min(3, len(options))])
                chosen_indexes = [options.index(x) for x in chosen]

                cols = st.columns(3)
                for p, idx in enumerate(chosen_indexes[:9]):
                    item = image_candidates[idx]
                    img = download_image_from_url(item["url"])
                    selected_images.append(img)
                    with cols[p % 3]:
                        st.image(img, caption=item["alt"] or "Bild", width=180)
            except Exception as e:
                st.error(f"Link konnte nicht geladen werden: {e}")

    st.session_state["selected_images"] = selected_images
    st.session_state["source_texts"] = source_texts

with tab2:
    st.subheader("Marketingbilder erstellen")

    selected_images = st.session_state.get("selected_images", [])
    source_texts = st.session_state.get("source_texts", [])

    if not selected_images:
        st.warning("Bitte zuerst in Tab 1 mindestens ein Produktbild auswählen oder hochladen.")
    else:
        st.success(f"{len(selected_images)} Produktbild(er) bereit.")

    source_text = st.text_area(
        "Produkt-/Markentext für Caption und Bildprompt",
        value=clean_text(" ".join(source_texts[:5]), 1200) if source_texts else "Elegante Stella Maris Uhren und Schmuck für besondere Momente.",
        height=120,
    )

    tags = st.text_area("Hashtags", value=DEFAULT_TAGS)

    create = st.button("Echte Marketingbilder generieren", type="primary")

    if create and selected_images:
        if not api_key:
            st.warning("Kein OpenAI API Key eingetragen. Ich erstelle deshalb Preview-Marketingbilder mit Produktbild + Slogan, aber keine echten AI-Modelbilder.")
        else:
            st.success("OpenAI API Key erkannt. Es werden AI-Marketingbilder generiert.")

        out_cols = st.columns(3)

        for i in range(int(amount)):
            product_img = selected_images[i % len(selected_images)]
            slogan = random.choice(SLOGANS)
            prompt = make_prompt(
                product_focus=product_focus,
                source_text=source_text,
                slogan=slogan,
                image_note="Use the selected Stella Maris product image as product inspiration.",
            )

            with out_cols[i % 3]:
                st.markdown(f"### Entwurf {i+1}")

                try:
                    if api_key:
                        ai_img = generate_ai_image(api_key, prompt)
                        jpg = convert_to_2000_jpg(ai_img, slogan=slogan)
                    else:
                        jpg = make_preview_card(product_img, slogan)

                    st.image(jpg, width=260)

                    st.download_button(
                        "JPG 2000×2000 herunterladen",
                        data=jpg.getvalue(),
                        file_name=f"stella_maris_marketing_{i+1}.jpg",
                        mime="image/jpeg",
                        key=f"dl_{i}",
                    )

                    with st.expander("Caption / Prompt / Video-Konzept"):
                        st.write("**Slogan:**")
                        st.write(slogan)
                        st.write("**Caption:**")
                        st.write(f"{slogan} {source_text[:220]} {tags}")
                        st.write("**Video-Konzept:**")
                        st.write("0–2 Sek.: Produkt-Close-up. 3–7 Sek.: elegantes Model trägt das Produkt. 8–12 Sek.: Geschenk-/Lifestyle-Szene. 13–15 Sek.: Stella Maris Logo + Slogan.")
                        st.write("**AI Prompt:**")
                        st.code(prompt)

                except Exception as e:
                    st.error(f"Entwurf {i+1} konnte nicht erstellt werden: {e}")

with tab3:
    st.subheader("Wichtig")
    st.write("- Ohne OpenAI API Key erstellt die App nur Preview-Bilder mit Produktbild + Slogan.")
    st.write("- Mit OpenAI API Key erstellt die App echte AI-Marketingbilder im Luxus-Stil.")
    st.write("- Download: JPG 2000 × 2000 px mit 300-DPI-Metadaten.")
    st.write("- Für echte Videos wird ein separater Video-Generator benötigt; diese App erstellt Video-Konzepte/Storyboards.")
