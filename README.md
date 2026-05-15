# Stella Maris Content Autopilot

Streamlit-App, die neue hochwertige Stella-Maris-Marketingbilder erzeugt,
edle Slogans direkt ins Bild schreibt und animierte Reel-Entwuerfe erstellt.

## Streamlit Cloud

1. ZIP entpacken.
2. Inhalt in dein GitHub-Repository hochladen.
3. In Streamlit Cloud das Repository auswaehlen.
4. Unter App > Settings > Secrets deinen OpenAI API-Key eintragen:

```toml
OPENAI_API_KEY = "dein_api_key"
```

5. Als Main file path eintragen:

```text
streamlit_app.py
```

6. Deploy starten.

## Enthalten

- `streamlit_app.py`
- `requirements.txt`
Die App generiert neue Bilder per OpenAI Image API. Ein `assets` Ordner ist
nicht mehr notwendig.
