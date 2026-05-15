import streamlit as st
from datetime import datetime, time
import random

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

MARKETING_HOOKS = [
    "Zeitlose Eleganz beginnt bei den Details.",
    "Luxus muss nicht laut sein.",
    "Ein eleganter Look beginnt am Handgelenk.",
    "Minimalistisch. Edel. Stella Maris.",
    "Die perfekte Kombination aus Schmuck und Stil.",
]

VISUAL_STYLES = [
    "Luxus-Lifestyle mit Marmor und Goldlicht",
    "Elegante Fashion-Kampagne mit weichen Schatten",
    "Premium Produktaufnahme mit hellem Studio-Licht",
    "Instagram Luxury Branding mit cleanem Hintergrund",
    "Cinematic Reel Style mit Detailaufnahmen",
]

VIDEO_IDEAS = [
    "Slow Motion Detailshots mit eleganter Musik",
    "Luxury Reel mit Outfit-Wechsel und Nahaufnahmen",
    "Produkt Showcase mit Zoom-Effekten",
    "UGC Premium Style mit natürlichem Licht",
    "Fashion Cinematic Video mit Close-Ups",
]

PRODUCT_TEXTS = [
    "Premium-Keramik, Saphirglas und zeitlose Eleganz.",
    "Elegante Schmuckstücke für besondere Momente.",
    "Luxuriöse Designs inspiriert von moderner Eleganz.",
    "Minimalistische Luxus-Uhren mit hochwertigen Materialien.",
]

def clean_tags(raw_tags):
    result = []
    for item in raw_tags.replace(",", " ").replace(";", " ").split():
        tag = item.strip().replace("#", "").lower()
        if tag and tag not in result:
            result.append(tag)
    return result[:30]

def is_safe_time(selected_time):
    return any(start <= selected_time <= end for _, start, end in SAFE_WINDOWS)

st.title("💎 Stella Maris AI Marketing Studio")
st.caption("Erstellt hochwertige Marketingbilder, Luxus-Reels, Captions und Social-Media-Kampagnen automatisch.")

st.warning(
    "Die App erstellt Marketing-Content und Luxus-Design-Ideen. "
    "Riskante Automatisierung wie Auto-Follow, Massen-DMs oder Spam-Aktionen bleibt deaktiviert."
)

st.divider()

left, right = st.columns([1, 1])

with left:
    st.subheader("Marketing-Generator")

    drafts = st.number_input(
        "Wie viele Entwürfe sollen erstellt werden?",
        min_value=1,
        max_value=50,
        value=5,
        step=1
    )

    content_type = st.selectbox(
        "Content-Art",
        [
            "Luxury Reel",
            "Marketing Bild",
            "Instagram Story",
            "TikTok Video",
            "Produktkampagne",
        ]
    )

    source_mode = st.radio(
        "Content-Quelle",
        [
            "Stella Maris Webseiten automatisch verwenden",
            "Eigene Bilder hochladen",
            "Externe Webseite verwenden",
        ]
    )

    if source_mode == "Stella Maris Webseiten automatisch verwenden":
        st.success("Verwendet stella-maris-world.de und stella-maris-world.com als Inspirationsquelle.")
        st.write("Quellen:")
        st.write("- https://www.stella-maris-world.de")
        st.write("- https://www.stella-maris-world.com")

    if source_mode == "Eigene Bilder hochladen":
        uploaded_files = st.file_uploader(
            "Eigene Produktbilder",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} Bild(er) hochgeladen")
            preview = st.columns(3)
            for i, file in enumerate(uploaded_files[:6]):
                with preview[i % 3]:
                    st.image(file, use_container_width=True)

    if source_mode == "Externe Webseite verwenden":
        external_url = st.text_input(
            "Webseiten-Link",
            placeholder="https://example.com"
        )

        if external_url:
            st.success(f"Quelle gespeichert: {external_url}")

    raw_tags = st.text_area(
        "Hashtags / Zielgruppen",
        value=DEFAULT_TAGS
    )

    tags = clean_tags(raw_tags)

    selected_time = st.time_input(
        "Geplante Posting-Zeit",
        value=datetime.now().time().replace(second=0, microsecond=0)
    )

    if is_safe_time(selected_time):
        st.success("Sicheres Posting-Zeitfenster erkannt.")
    else:
        st.error("Diese Uhrzeit liegt außerhalb der empfohlenen Zeiten.")

    generate = st.button("Luxury Content generieren", type="primary")

with right:
    st.subheader("Luxus-Marketing Features")

    st.markdown("### ✨ Automatische Luxus-Positionierung")
    st.write("Produkte werden mit hochwertigen Hintergründen, eleganten Schatten und Premium-Lifestyle-Optik dargestellt.")

    st.markdown("### 🎬 Video- & Reel-Konzepte")
    st.write("Automatische Reel-Strukturen mit Hooks, Kameraideen und CTA-Vorschlägen.")

    st.markdown("### 🖼️ Marketingbild-Konzepte")
    st.write("Luxus-Kampagnen mit Produktfokus, Fashion-Look und Premium-Branding.")

    st.markdown("### 📈 Social-Media-Wachstum")
    st.write("Captions, Hashtags und Kampagnen-Ideen für Instagram, TikTok und Pinterest.")

st.divider()

if generate:
    st.subheader("Generierte Luxus-Entwürfe")

    all_text = []

    for i in range(int(drafts)):
        hook = random.choice(MARKETING_HOOKS)
        visual = random.choice(VISUAL_STYLES)
        video = random.choice(VIDEO_IDEAS)
        product_text = random.choice(PRODUCT_TEXTS)
        hashtags = " ".join([f"#{tag}" for tag in tags[:10]])

        caption = f"{hook} {product_text} #stellamaris #luxurywatch #schmuckliebe"
        marketing = (
            f"Positioniere die Uhr oder den Schmuck zentral mit {visual.lower()}, "
            "hochwertigen Reflexionen, cleanem Luxus-Hintergrund und eleganter Fashion-Atmosphäre."
        )
        reel = (
            f"Nutze {video.lower()}, langsame Kamerafahrten, Detailshots "
            "und elegante Übergänge mit Luxus-Musik."
        )
        prompt = (
            f"Luxury Stella Maris campaign, premium jewelry and watches, elegant studio lighting, "
            f"luxury fashion style, ultra realistic, Instagram luxury branding, {visual}"
        )

        with st.container(border=True):
            st.markdown(f"## {content_type} {i+1}")

            st.markdown("### Caption")
            st.write(caption)

            st.markdown("### Marketingbild-Konzept")
            st.write(marketing)

            st.markdown("### Video-/Reel-Konzept")
            st.write(reel)

            st.markdown("### KI-Bildprompt")
            st.code(prompt)

            st.markdown("### Hashtags")
            st.write(hashtags)

        all_text.append(
            f"{content_type} {i+1}\n\n"
            f"Caption:\n{caption}\n\n"
            f"Marketingbild-Konzept:\n{marketing}\n\n"
            f"Video-/Reel-Konzept:\n{reel}\n\n"
            f"KI-Bildprompt:\n{prompt}\n\n"
            f"Hashtags:\n{hashtags}\n\n"
            "----------------------------------------\n\n"
        )

    st.download_button(
        "Alle Entwürfe als TXT herunterladen",
        data="".join(all_text),
        file_name="stella_maris_marketing_entwuerfe.txt",
        mime="text/plain"
    )

st.divider()

st.subheader("Empfohlene sichere Posting-Zeiten")
for name, start, end in SAFE_WINDOWS:
    st.write(f"**{name}:** {start.strftime('%H:%M')}–{end.strftime('%H:%M')}")

st.info(
    "Die App kann mit eigenen Bildern, Webseiten oder Stella-Maris-Inhalten verwendet werden "
    "und erstellt daraus Luxus-Marketing-Kampagnen."
)
