# Stella Maris Content Autopilot

Streamlit-App fuer Stella Maris, die neue Premium-Marketingmotive erzeugt:

- frei waehlbare Anzahl von 0 bis 10 Bildentwuerfen pro Kampagne
- 5 Slogan-Entwuerfe mit Button fuer neue 5 Vorschlaege
- Slogan und CTA direkt im Bild, ohne transparente Textbox
- Aenderungsfeld pro Entwurf, um das Bild anhand deiner Beschreibung bearbeiten oder neu generieren zu lassen
- ca. 20 Sekunden MP4-Reel aus den erzeugten Entwuerfen

Die App nutzt keine festen Asset-Bilder. Die Bilder werden ueber die OpenAI Image API neu erzeugt. Es sind mehrere Motive fuer Geschenk, Business, Abend, Reise, Hochzeit, Muttertag, Cafe, Beauty, Gala, Resort und Detailkampagnen enthalten.

## Streamlit Cloud

1. Diese Dateien in dein GitHub-Repository hochladen:
   - `app.py`
   - `streamlit_app.py`
   - `requirements.txt`
   - `README.md`
2. In Streamlit Cloud das Repository auswaehlen.
3. Als Main file path verwenden:

```text
streamlit_app.py
```

Wenn dein Projekt schon `app.py` als Startdatei nutzt, kannst du auch `app.py` lassen.

4. Unter App > Settings > Secrets den OpenAI API-Key eintragen:

```toml
OPENAI_API_KEY = "dein_api_key"
```

5. Deploy starten oder die App neu starten.

## Wichtig

Der Ordner `assets` muss nicht hochgeladen werden. Die App erstellt neue Bilder und ein Video direkt in Streamlit.
