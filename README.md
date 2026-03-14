\# 🎙️ LessonCast



Convert any text or lesson script into a podcast-style audio file.

Runs 100% locally — no cloud, no API keys, no data leaves your machine.



Powered by Kokoro-TTS.



\---



\## ⬇️ Download \& Run (no Python needed)



| Platform | Download |

|---|---|

| Windows | LessonCast-Windows.zip |

| Mac (M1/M2/M3) | LessonCast-Mac-ARM.zip |

| Mac (Intel) | LessonCast-Mac-Intel.zip |



1\. Unzip

2\. Mac: run ./start.sh — Windows: double-click start.bat

3\. Browser opens at http://localhost:5000

4\. Paste your script → pick a voice → Generate 🎉



First launch takes \~30 seconds while the AI model loads.



\---



\## 🛠️ Run from source (developers)



```

git clone https://github.com/YOU/lessoncast.git

cd lessoncast

python -m venv venv \&\& source venv/bin/activate

pip install flask flask-cors soundfile numpy kokoro

python app.py

```



