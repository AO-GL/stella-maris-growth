import streamlit as st
from datetime import datetime, time

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

LIMITS = {
    "Posts/Reels": 2,
    "Stories": 5,
    "Manuelle Aufgaben": 20,
}

CONTENT_IDEAS = [
    {
        "type": "Reel",
        "title": "3 Gründe für Stella Maris",
        "caption": "Zeitlose Eleganz trifft auf echte Details. Welche Uhr passt zu deinem Stil? ✨ #stellamaris #uhrenliebe #damenuhr",
    },
    {
        "type": "Story",
        "title": "Umfrage: Gold, Silber oder Keramik?",
        "caption": "Heute im Fokus: edle Materialien, klare Linien und ein Look, der jeden Tag funktioniert.",
    },
    {
        "type": "Post",
        "title": "Geschenkidee für besondere Momente",
        "caption": "Ein Schmuckstück sagt oft mehr als viele Worte. Entdecke Stella Maris für elegante Geschenkideen.",
    },
]

DEFAULT_TAGS = "damenuhr schmuckliebe geschenkidee uhrenliebe stellamaris diamantschmuck keramikuhr"

def is_safe_time(selected_time):
    return any(start <= selected_time <= end for _, start, end in SAFE_WINDOWS)

def next_safe_window(selected_time):
    for name, start, end in SAFE_WINDOWS:
        if selected_time < start:
            return name, start, end
    return SAFE_WINDOWS[0]

def clean_tags(raw_tags):
    result = []
    for item in raw_tags.replace(",", " ").replace(";", " ").split():
        tag = item.strip().replace("#", "").lower()
        if tag and tag not in result:
            result.append(tag)
    return result[:20]

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"type": "Reel", "text": "Reel-Idee zu Premium-Keramik vorbereiten", "time": "17:45", "done": False},
        {"type": "Story", "text": "Story-Umfrage: Welche Uhr passt zu dir?", "time": "12:15", "done": False},
    ]

st.title("💎 Stella Maris Growth App")
st.caption("Sicherer Social-Media-Planer für Wachstum durch Content und echte Interaktion.")

st.warning(
    "Keine Auto-Follows, Auto-Likes oder Massen-DMs. "
    "Die App unterstützt nur sichere Growth-Methoden."
)

col1, col2, col3 = st.columns(3)

posts_count = sum(1 for t in st.session_state.tasks if t["type"] in ["Post", "Reel"])
stories_count = sum(1 for t in st.session_state.tasks if t["type"] == "Story")
manual_count = sum(1 for t in st.session_state.tasks if t["type"] == "Manuell")

col1.metric("Posts/Reels", f"{posts_count}/{LIMITS['Posts/Reels']}")
col2.metric("Stories", f"{stories_count}/{LIMITS['Stories']}")
col3.metric("Manuelle Aufgaben", f"{manual_count}/{LIMITS['Manuelle Aufgaben']}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Neue Aufgabe")

    raw_tags = st.text_area(
        "Hashtags / Zielgruppen",
        value=DEFAULT_TAGS
    )

    tags = clean_tags(raw_tags)

    action = st.selectbox(
        "Aktion",
        [
            "Reel vorbereiten",
            "Post vorbereiten",
            "Story vorbereiten",
            "Manuelle Profil-Interaktion",
        ]
    )

    selected_time = st.time_input(
        "Uhrzeit",
        value=datetime.now().time().replace(second=0, microsecond=0)
    )

    if is_safe_time(selected_time):
        st.success("Diese Uhrzeit liegt im sicheren Zeitfenster.")
        planned_time = selected_time
    else:
        name, start, end = next_safe_window(selected_time)
        st.error(f"Außerhalb der sicheren Zeiten. Automatisch auf {start.strftime('%H:%M')} verschoben.")
        planned_time = start

    if st.button("Aufgabe hinzufügen"):
        first_tag = tags[0] if tags else "stellamaris"

        if action == "Manuelle Profil-Interaktion":
            task = {
                "type": "Manuell",
                "text": f"Passende Profile über #{first_tag} prüfen und echte Kommentare vorbereiten.",
                "time": planned_time.strftime("%H:%M"),
                "done": False,
            }
        elif action == "Story vorbereiten":
            task = {
                "type": "Story",
                "text": f"Story-Idee für #{first_tag} vorbereiten.",
                "time": planned_time.strftime("%H:%M"),
                "done": False,
            }
        elif action == "Post vorbereiten":
            task = {
                "type": "Post",
                "text": f"Post zu #{first_tag} vorbereiten.",
                "time": planned_time.strftime("%H:%M"),
                "done": False,
            }
        else:
            task = {
                "type": "Reel",
                "text": f"Reel zu #{first_tag} vorbereiten.",
                "time": planned_time.strftime("%H:%M"),
                "done": False,
            }

        st.session_state.tasks.insert(0, task)
        st.rerun()

with right:
    st.subheader("Tagesplan")

    for i, task in enumerate(st.session_state.tasks):
        with st.container(border=True):
            done = st.checkbox(
                f"{task['time']} · {task['type']} · {task['text']}",
                value=task["done"],
                key=f"task_{i}"
            )

            st.session_state.tasks[i]["done"] = done

st.divider()

st.subheader("Content-Ideen")

for idea in CONTENT_IDEAS:
    with st.container(border=True):
        st.markdown(f"### {idea['title']}")
        st.write(idea["caption"])

st.info(
    "Upload diese app.py und requirements.txt zu GitHub und deploye danach auf Streamlit Cloud."
)
