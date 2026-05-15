import base64
import mimetypes
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).parent


def data_uri(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def load_app() -> str:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "app.js").read_text(encoding="utf-8")

    for asset in (ROOT / "assets").glob("*"):
        if asset.is_file():
            js = js.replace(f"assets/{asset.name}", data_uri(asset))

    html = html.replace('<link rel="stylesheet" href="styles.css" />', f"<style>{css}</style>")
    html = html.replace('<script src="app.js"></script>', f"<script>{js}</script>")
    return html


st.set_page_config(page_title="Stella Maris Growth Chatbot", layout="wide")
components.html(load_app(), height=2600, scrolling=True)
