# 🎙️ LessonCast

Convert any text or lesson script into a podcast-style audio file.
Runs **100% locally** — no cloud, no API keys, no data leaves your machine.

Powered by [Kokoro-TTS](https://github.com/hexgrad/kokoro).

---

## ⬇️ Download & Run (no Python needed)

| Platform | Download |
|---|---|
| Windows | [LessonCast-Windows.zip](https://github.com/Abdo-develloper-Keraoui/lessoncast/releases/latest) |

1. Unzip
   **Windows:** double-click `start.bat`
2. Browser opens automatically at `http://localhost:5000`
3. Paste your script → pick a voice → hit Generate 🎉

> ⚠️ First launch takes ~30 seconds while the AI model loads. Don't close the terminal window.

---

## 🛠️ Run from source (developers)
```bash
git clone https://github.com/Abdo-develloper-Keraoui/lessoncast.git
cd lessoncast
python -m venv venv && source venv/bin/activate
pip install flask flask-cors soundfile numpy kokoro
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## 🎤 Voices

| Voice | Gender | Accent |
|---|---|---|
| Heart, Bella, Nicole, Sarah, Sky | Female | American English |
| Adam, Michael | Male | American English |
| Emma, Isabella | Female | British English |
| George, Lewis | Male | British English |
| Siwis | Female | French |

---

## 📄 License

MIT — free to use, modify, and distribute.