import streamlit as st
from datetime import datetime, time
import random

st.set_page_config(
    page_title="Stella Maris Growth App",
    page_icon="💎",
    layout="wide"
)

SAFE_WINDOWS = [
    ("Morgen", time(8, 0), time(10, 0)),
    ("Mittag", time(12, 0), time(14, 0)),
    ("Abend", time(17, 30), time(20, 30)),
]

HOOKS = [
    "Diese Uhr passt zu jedem eleganten Outfit.",
    "Ein Schmuckstück, das sofort hochwertig wirkt.",
    "Warum kleine Details den ganzen Look verändern.",
    "So kombinierst du Uhr und Schmuck stilvoll.",
    "Geschenkidee, die persönlich und edel wirkt.",
    "Zeitlose Eleganz für jeden Tag.",
]

VISUAL_IDEAS = [
    "Nahaufnahme der Uhr auf hellem Marmor mit weichem Licht",
    "Schmuckstück in einer eleganten Geschenkbox",
    "Uhr am Handgelenk mit Business-Outfit",
    "Flatlay mit Uhr, Schmuck, Parfum und Seide",
    "Vorher/Nachher Styling: schlichtes Outfit vs. Stella Maris Look",
    "Detailaufnahme von Keramik, Saphirglas oder Perlmutt",
]

VIDEO_STRUCTURES = [
    "0-2 Sek.: starker Hook, 3-7 Sek.: Produktdetail, 8-12 Sek.: Styling, 13-15 Sek.: CTA",
    "0-3 Sek.: Geschenkproblem zeigen, 4-9 Sek.: Stella Maris als Lösung, 10-15 Sek.: Close-up + CTA",
    "0-2 Sek.: Frage stellen, 3-10 Sek.: 3 Vorteile zeigen, 11-15 Sek.: Kommentar-CTA",
    "0-4 Sek.: Lifestyle-Szene, 5-10 Sek.: Produktdetails, 11-15 Sek.: Shop-/Profilhinweis",
]

CAPTION_STARTS = [
    "Zeitlose Eleganz trifft auf moderne Details.",
    "Für Momente, in denen dein Look besonders wirken soll.",
    "Ein kleines Detail kann den ganzen Stil verändern.",
    "Stella Maris steht für elegante Uhren und Schmuck mit Charakter.",
    "Perfekt als Geschenk oder als tägliches Statement.",
]

DEFAULT_TAGS = "damenuhr schmuckliebe geschenkidee uhrenliebe stellamaris diamantschmuck keramikuhr luxusaccessoires"

def clean_tags(raw_tags):
    result = []
    for item in raw_tags.replace(",", " ").replace(";", " ").split():
        tag = item.strip().replace("#", "").lower()
        if tag and tag not in result:
            result.append(tag)
    return result[:30]

def is_safe_time(selected_time):
    return any(start <= selected_time <= end for _, start, end in SAFE_WINDOWS)

def next_safe_window(selected_time):
    for name, start, end in SAFE_WINDOWS:
        if selected_time < start:
            return name, start, end
    return SAFE_WINDOWS[0]

def generate_draft(index, tags, product_focus, content_type):
    tag_string = " ".join([f"#{t}" for t in tags[:8]])
    hook = random.choice(HOOKS)
    visual = random.choice(VISUAL_IDEAS)
    video = random.choice(VIDEO_STRUCTURES)
    caption_start = random.choice(CAPTION_STARTS)

    if content_type == "Reel / Video":
        title = f"Reel-Entwurf {index}: {hook}"
        script = f"""
Szene 1: {hook}
Szene 2: Zeige {product_focus} als Close-up.
Szene 3: Kurzer Styling-Moment mit elegantem Outfit.
Szene 4: CTA: „Folge Stella Maris für mehr elegante Looks.“
Timing: {video}
"""
        image_prompt = f"Erstelle ein elegantes Social-Media-Bild für Stella Maris: {visual}, Fokus auf {product_focus}, luxuriös, hell, clean, hochwertig, Instagram-ready."
    elif content_type == "Bild-Post":
        title = f"Bild-Post-Entwurf {index}: {product_focus}"
        script = "Bildidee: " + visual
        image_prompt = f"Eleganter Instagram-Post für Stella Maris, {visual}, Produktfokus {product_focus}, luxuriöses Schmuck- und Uhren-Branding, hochwertig, clean."
    else:
        title = f"Story-Entwurf {index}: Interaktion"
        script = f"Story 1: Frage: Gold, Silber oder Keramik? Story 2: Zeige {product_focus}. Story 3: Umfrage-Sticker oder CTA."
        image_prompt = f"Instagram Story Design für Stella Maris, {visual}, Fokus auf {product_focus}, vertikales Format, elegant."

    caption = f"{caption_start} {hook} Entdecke {product_focus} von Stella Maris. {tag_string}"

    return {
        "title": title,
        "content_type": content_type,
        "caption": caption,
        "script": script.strip(),
        "image_prompt": image_prompt,
        "hashtags": tag_string,
    }

st.title("💎 Stella Maris Growth App")
st.caption("Erstellt Social-Media-Entwürfe für Posts, Bilder, Stories und Reels.")

st.warning(
    "Sicherheitsregel: Keine Auto-Follows, Auto-Likes, Auto-Kommentare oder Massen-DMs. "
    "Die App erstellt Content-Entwürfe und sichere manuelle Aufgaben."
)

st.divider()

col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("1. Entwürfe einstellen")

    draft_count = st.number_input(
        "Wie viele Entwürfe sollen erstellt werden?",
        min_value=1,
        max_value=50,
        value=5,
        step=1
    )

    content_type = st.selectbox(
        "Welche Art Content?",
        ["Reel / Video", "Bild-Post", "Story"]
    )

    product_focus = st.selectbox(
        "Produkt-Fokus",
        [
            "Damenuhren",
            "Schmuck",
            "Uhren & Schmuck Set",
            "Keramikuhren",
            "Diamantschmuck",
            "Geschenkideen",
            "Elegante Accessoires",
        ]
    )

    raw_tags = st.text_area(
        "Hashtags / Zielgruppen",
        value=DEFAULT_TAGS
    )

    tags = clean_tags(raw_tags)
    st.write("Aktive Hashtags:")
    st.write(" ".join([f"#{tag}" for tag in tags]))

with col_b:
    st.subheader("2. Produktbilder hochladen")

    uploaded_files = st.file_uploader(
        "Lade Produktbilder hoch, damit du sie später für Posts/Reels nutzen kannst.",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} Bild(er) hochgeladen.")
        preview_cols = st.columns(3)
        for i, file in enumerate(uploaded_files[:6]):
            with preview_cols[i % 3]:
                st.image(file, caption=file.name, use_container_width=True)
    else:
        st.info("Noch keine Bilder hochgeladen. Du kannst die App aber trotzdem für Entwürfe nutzen.")

st.divider()

st.subheader("3. Posting-Zeit prüfen")

selected_time = st.time_input(
    "Geplante Uhrzeit",
    value=datetime.now().time().replace(second=0, microsecond=0)
)

if is_safe_time(selected_time):
    st.success("Diese Uhrzeit liegt in einem üblichen sicheren Posting-Zeitfenster.")
else:
    name, start, end = next_safe_window(selected_time)
    st.error(f"Diese Uhrzeit ist nicht ideal. Vorschlag: {name} zwischen {start.strftime('%H:%M')} und {end.strftime('%H:%M')}.")

with st.expander("Empfohlene Posting-Zeitfenster anzeigen"):
    for name, start, end in SAFE_WINDOWS:
        st.write(f"**{name}:** {start.strftime('%H:%M')}–{end.strftime('%H:%M')}")

st.divider()

if st.button("Entwürfe jetzt erstellen", type="primary"):
    st.session_state.generated_drafts = [
        generate_draft(i + 1, tags, product_focus, content_type)
        for i in range(int(draft_count))
    ]

if "generated_drafts" in st.session_state:
    st.subheader("4. Generierte Entwürfe")

    all_text = []

    for draft in st.session_state.generated_drafts:
        with st.container(border=True):
            st.markdown(f"### {draft['title']}")
            st.markdown(f"**Typ:** {draft['content_type']}")

            st.markdown("**Caption:**")
            st.write(draft["caption"])

            st.markdown("**Video-/Post-Skript:**")
            st.write(draft["script"])

            st.markdown("**Bild-Idee / KI-Bild-Prompt:**")
            st.code(draft["image_prompt"])

            st.markdown("**Hashtags:**")
            st.write(draft["hashtags"])

            all_text.append(
                f"{draft['title']}\n\n"
                f"Typ: {draft['content_type']}\n\n"
                f"Caption:\n{draft['caption']}\n\n"
                f"Skript:\n{draft['script']}\n\n"
                f"Bild-Prompt:\n{draft['image_prompt']}\n\n"
                f"Hashtags:\n{draft['hashtags']}\n\n"
                "----------------------------------------\n\n"
            )

    st.download_button(
        "Alle Entwürfe als TXT herunterladen",
        data="".join(all_text),
        file_name="stella_maris_entwuerfe.txt",
        mime="text/plain"
    )

st.divider()

st.subheader("Was diese App macht")
st.write(
    "- fragt immer, wie viele Entwürfe erstellt werden sollen\n"
    "- erstellt Captions, Hashtags, Bildideen und Reel-Skripte\n"
    "- erlaubt Produktbild-Uploads\n"
    "- prüft sichere Posting-Zeiten\n"
    "- blockiert riskante Automatisierung wie Auto-Follow oder Massen-DM"
)
