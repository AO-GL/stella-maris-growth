import streamlit as st
from datetime import datetime, time
from PIL import Image, ImageDraw, ImageFont
import random
import os

st.set_page_config(
    page_title="Stella Maris AI Marketing Studio",
    page_icon="💎",
    layout="wide"
)

SAFE_WINDOWS = [
    ("Morgen", time(8, 0), time(10, 0)),
    ("Mittag", time(12, 0), time(14, 0)),
    ("Abend", time(17, 30), time(20, 30)),
]

DEFAULT_TAGS = "stellamaris damenuhr schmuckliebe luxurywatch elegantschmuck premiumstyle keramikuhr"

captions = [
    "Zeitlose Eleganz trifft modernes Luxusdesign.",
    "Luxus beginnt bei den Details.",
    "Elegante Schmuckstücke für besondere Momente.",
    "Minimalistische Luxury-Watches für starke Looks.",
    "Premium Style für jeden Tag."
]

marketing_concepts = [
    "Elegante Luxus-Kampagne mit weichen Schatten und hochwertiger Fashion-Atmosphäre.",
    "Minimalistisches Premium-Design mit luxuriösen Reflexionen.",
    "Goldene Lichtstimmung mit edler Schmuck-Inszenierung.",
    "Hochwertiges Studio-Setup mit Fashion-Luxury-Look."
]

video_concepts = [
    "Slow-Motion Nahaufnahme mit sanften Kamerafahrten.",
    "Luxury Reel mit Detailshots und eleganter Musik.",
    "Fashion-Reel mit Fokus auf hochwertige Materialien.",
    "Instagram Luxury Campaign mit weichen Übergängen."
]

st.title("💎 Stella Maris Growth App")
st.caption("AI Marketing Generator für Bilder, Reels und Luxus-Content")

st.warning(
    "Keine Auto-Follows oder Spam-Aktionen. "
    "Die App erstellt sichere Marketing-Entwürfe."
)

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input(
        "Wie viele Entwürfe erstellen?",
        min_value=1,
        max_value=20,
        value=5
    )

    content_type = st.selectbox(
        "Welche Art Content?",
        ["Marketing Bilder", "Reel / Video", "Story", "Luxury Kampagne"]
    )

    product_focus = st.selectbox(
        "Produkt Fokus",
        [
            "Damenuhren",
            "Luxus Schmuck",
            "Keramikuhren",
            "Diamantschmuck",
            "Premium Fashion"
        ]
    )

    hashtags = st.text_area(
        "Hashtags / Zielgruppe",
        DEFAULT_TAGS
    )

with col2:
    uploaded = st.file_uploader(
        "Eigene Produktbilder hochladen (JPG)",
        type=["jpg", "jpeg"]
    )

posting_time = st.time_input(
    "Geplante Posting Zeit",
    value=datetime.now().time()
)

safe = False

for name, start, end in SAFE_WINDOWS:
    if start <= posting_time <= end:
        safe = True

if safe:
    st.success("Sicheres Posting-Zeitfenster erkannt.")
else:
    st.error("Ungewöhnliche Uhrzeit. Nutze besser typische Aktivitätszeiten.")

generate = st.button("Luxury Content generieren")

if generate:

    st.header("Generierte Luxus-Entwürfe")

    os.makedirs("generated", exist_ok=True)

    for i in range(amount):

        caption = random.choice(captions)
        marketing = random.choice(marketing_concepts)
        video = random.choice(video_concepts)

        img = Image.new("RGB", (1080, 1350), color=(18, 18, 18))

        draw = ImageDraw.Draw(img)

        draw.rectangle(
            [(40, 40), (1040, 1310)],
            outline=(212, 175, 55),
            width=5
        )

        title = "STELLA MARIS"

        text = f"""
{product_focus}

{caption}

Luxury Collection
"""

        try:
            font_big = ImageFont.truetype("arial.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 36)
        except:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text(
            (120, 120),
            title,
            fill=(212, 175, 55),
            font=font_big
        )

        draw.text(
            (120, 320),
            text,
            fill=(255, 255, 255),
            font=font_small
        )

        file_name = f"generated/stella_maris_{i+1}.jpg"

        img.save(file_name, quality=95)

        st.subheader(f"Marketing Bild {i+1}")

        st.image(file_name)

        with open(file_name, "rb") as file:
            st.download_button(
                label=f"JPG herunterladen {i+1}",
                data=file,
                file_name=f"stella_maris_{i+1}.jpg",
                mime="image/jpeg"
            )

        st.markdown("### Caption")
        st.write(caption)

        st.markdown("### Marketingbild-Konzept")
        st.write(marketing)

        st.markdown("### Video-/Reel-Konzept")
        st.write(video)

        st.markdown("### Hashtags")
        st.code(
            "#stellamaris #luxurywatch #schmuckliebe "
            "#premiumstyle #luxuryfashion"
        )

        st.divider()
