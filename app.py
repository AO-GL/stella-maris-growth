from pathlib import Path
import zipfile

app_code = r'''import streamlit as st
from datetime import datetime, time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

st.set_page_config(
    page_title="Stella Maris Content Studio",
    page_icon="💎",
    layout="wide"
)

SAFE_WINDOWS = [
    ("Morgen", time(8, 0), time(10, 0)),
    ("Mittag", time(12, 0), time(14, 0)),
    ("Abend", time(17, 30), time(20, 30)),
]

CAPTIONS = [
    "Zeitlose Eleganz trifft modernes Luxusdesign.",
    "Luxus beginnt bei den Details.",
    "Elegante Schmuckstücke für besondere Momente.",
    "Premium Style für jeden Tag.",
    "Minimalistische Eleganz mit Stella Maris.",
]

CONCEPTS = [
    "Clean Luxury Kampagne mit hellem Hintergrund und goldenen Akzenten.",
    "Premium Fashion Look mit eleganter Produktpositionierung.",
    "Minimalistisches Schmuck-Design mit starker Markenwirkung.",
    "Instagram Luxury Campaign mit hochwertiger Typografie.",
]

VIDEO_CONCEPTS = [
    "0–2 Sek.: Hook, 3–7 Sek.: Produkt-Close-up, 8–12 Sek.: Styling, 13–15 Sek.: CTA.",
    "Slow-Motion Detailshots, elegante Musik, Close-up auf Uhr/Schmuck, Call-to-Action am Ende.",
    "Fashion Reel mit Outfit-Wechsel, Produktdetail und finalem Markenbild.",
]

DEFAULT_TAGS = "#stellamaris #luxurywatch #schmuckliebe #premiumstyle #luxuryfashion"


def is_safe_time(selected_time):
    return any(start <= selected_time <= end for _, start, end in SAFE_WINDOWS)


def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arial.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def make_square_image(index, product_focus, caption, concept, uploaded_image=None):
    # 2000 x 2000 px JPG, saved with 300 DPI metadata
    W, H = 2000, 2000
    bg = Image.new("RGB", (W, H), (245, 242, 235))
    draw = ImageDraw.Draw(bg)

    gold = (181, 139, 54)
    dark = (28, 28, 30)
    soft = (232, 226, 214)

    # background shapes
    draw.rectangle((0, 0, W, H), fill=(248, 246, 240))
    draw.ellipse((-350, -300, 900, 900), fill=soft)
    draw.ellipse((1250, 1100, 2300, 2200), fill=(238, 232, 220))
    draw.rectangle((90, 90, W - 90, H - 90), outline=gold, width=8)

    title_font = get_font(92)
    sub_font = get_font(52)
    small_font = get_font(38)
    tiny_font = get_font(30)

    draw.text((150, 150), "STELLA MARIS", fill=dark, font=title_font)
    draw.line((150, 270, 700, 270), fill=gold, width=8)

    # product image area
    product_box = (420, 390, 1580, 1320)
    if uploaded_image is not None:
        img = Image.open(uploaded_image).convert("RGB")
        img.thumbnail((1050, 850))
        x = (W - img.width) // 2
        y = 450
        shadow = Image.new("RGBA", (img.width + 80, img.height + 80), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse((35, img.height + 20, img.width + 45, img.height + 55), fill=(0, 0, 0, 55))
        bg.paste(shadow.convert("RGB"), (x - 40, y - 40))
        bg.paste(img, (x, y))
    else:
        # elegant placeholder product presentation
        draw.ellipse((720, 460, 1280, 1020), outline=gold, width=18)
        draw.ellipse((820, 560, 1180, 920), outline=(70, 70, 75), width=10)
        draw.rectangle((945, 1020, 1055, 1260), fill=(70, 70, 75))
        draw.ellipse((880, 1220, 1120, 1460), outline=gold, width=12)

    draw.text((150, 1410), product_focus.upper(), fill=gold, font=sub_font)
    draw.text((150, 1500), caption, fill=dark, font=small_font)

    # wrap concept
    words = concept.split()
    lines = []
    line = ""
    for word in words:
        if len(line + " " + word) < 62:
            line = (line + " " + word).strip()
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    y = 1590
    for line in lines[:3]:
        draw.text((150, y), line, fill=(80, 80, 85), font=tiny_font)
        y += 48

    draw.text((150, 1840), "Luxury Collection · Social Media Ready", fill=gold, font=tiny_font)

    out = BytesIO()
    bg.save(out, format="JPEG", quality=95, dpi=(300, 300))
    out.seek(0)
    return out


st.title("💎 Stella Maris Content Studio")
st.caption("Erstellt direkt sichtbare JPG-Marketingbilder, Captions und Reel-Konzepte.")

st.warning("Keine Auto-Follows, keine Massen-DMs, kein Spam. Nur Content-Erstellung.")

left, right = st.columns([0.9, 1.1])

with left:
    st.subheader("1. Einstellungen")

    amount = st.number_input("Wie viele Entwürfe erstellen?", min_value=1, max_value=20, value=5)
    product_focus = st.selectbox(
        "Produkt-Fokus",
        ["Damenuhren", "Luxus Schmuck", "Keramikuhren", "Diamantschmuck", "Uhren & Schmuck Set"]
    )

    uploaded_files = st.file_uploader(
        "Optional: eigene Produktbilder hochladen, JPG/JPEG",
        type=["jpg", "jpeg"],
        accept_multiple_files=True
    )

    hashtags = st.text_area("Hashtags", value=DEFAULT_TAGS)

    posting_time = st.time_input("Geplante Posting-Zeit", value=datetime.now().time().replace(second=0, microsecond=0))
    if is_safe_time(posting_time):
        st.success("Sicheres Posting-Zeitfenster erkannt.")
    else:
        st.error("Besser zu üblichen Zeiten posten: 08–10, 12–14 oder 17:30–20:30.")

    generate = st.button("JPG-Marketingbilder generieren", type="primary")

with right:
    st.subheader("2. Ergebnis")
    st.info("In der App werden nur kleine Thumbnails angezeigt. Der Download ist als 2000 × 2000 px JPG mit 300-DPI-Metadaten.")

if generate:
    st.divider()
    st.subheader("Generierte Marketingbilder")

    cols = st.columns(3)

    for i in range(int(amount)):
        caption = random.choice(CAPTIONS)
        concept = random.choice(CONCEPTS)
        video = random.choice(VIDEO_CONCEPTS)

        upload = None
        if uploaded_files:
            upload = uploaded_files[i % len(uploaded_files)]

        img_bytes = make_square_image(i + 1, product_focus, caption, concept, upload)

        with cols[i % 3]:
            st.markdown(f"### Entwurf {i+1}")

            # Thumbnail only
            st.image(img_bytes, width=260)

            st.download_button(
                "JPG 2000×2000 herunterladen",
                data=img_bytes.getvalue(),
                file_name=f"stella_maris_marketing_{i+1}.jpg",
                mime="image/jpeg",
                key=f"download_{i}"
            )

            with st.expander("Caption / Reel-Konzept"):
                st.write("**Caption:**")
                st.write(caption)
                st.write("**Marketing-Konzept:**")
                st.write(concept)
                st.write("**Reel-Konzept:**")
                st.write(video)
                st.write("**Hashtags:**")
                st.code(hashtags)
'''

requirements = """streamlit
pillow
"""

readme = """# Stella Maris Content Studio

Streamlit App.

Startdatei: app.py

Upload bei GitHub:
- app.py
- requirements.txt
- README.md
"""

base = Path("/mnt/data/stella_maris_content_studio_v3")
base.mkdir(exist_ok=True)
(base / "app.py").write_text(app_code, encoding="utf-8")
(base / "requirements.txt").write_text(requirements, encoding="utf-8")
(base / "README.md").write_text(readme, encoding="utf-8")

zip_path = "/mnt/data/stella_maris_content_studio_v3.zip"
with zipfile.ZipFile(zip_path, "w") as z:
    for f in base.iterdir():
        z.write(f, arcname=f.name)

print(zip_path)
