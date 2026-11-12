# Little Moon — CBSE Classes 1–8

**Little Moon** is an independent Streamlit learning app for CBSE learners in Classes 1–8, created by **NilanjanC**. It has its own GitHub repository and app entry point, separate from Little Sun. Students choose a class, subject and suggested chapter, or enter a chapter from their school syllabus. Activities include key words, fresh multiple-choice practice with explanations, custom-mark timed question papers, PDF downloads, and fun facts.

The broad chapter suggestions are CBSE/NCERT-aligned examples. Schools may use different textbooks, subject combinations or chapter names, so students can enter their own topic. English and Bengali are the language subjects offered; other generated content is in English. These suggestions are not a substitute for a school's current syllabus.

## Run locally

1. Install Python 3.12.
2. Create and activate a virtual environment: `python -m venv .venv` then `.venv\\Scripts\\Activate.ps1` (Windows) or `source .venv/bin/activate` (macOS/Linux).
3. Install dependencies: `pip install -r requirements.txt`.
4. Set `GEMINI_API_KEY` in `.streamlit/secrets.toml` or as an environment variable.
5. Run `streamlit run app.py`.

Example `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key"
```

Never commit a real API key. Add it to the app's Secrets in Streamlit Community Cloud instead.

## Deploy this as its own Streamlit app

1. In Streamlit Community Cloud, create an app from repository **`75neel-ops/little-moon`**, branch **`main`**, main file **`app.py`**.
2. Add `GEMINI_API_KEY` under this app's **Settings → Secrets**.
3. Deploy. This is a distinct deployment with no runtime or repo dependency on Little Sun.

The desktop and mobile install page will use Little Moon's own moon icon and name. The Razorpay button uses the public payment button ID supplied by the owner; do not add Razorpay secret keys here.

## Question freshness

Generated questions use `gemini-3.5-flash-lite`. Repeated wording is filtered within the current browser session and activity. Without shared storage, Little Moon cannot guarantee questions never repeat across different students or later sessions.

## Curriculum references

- [NCERT textbooks and Grades I–VIII catalogue](https://ncert.nic.in/textbook.php)
- [NCERT Bridge Programme](https://ncert.nic.in/bridge_programme.php)
- [CBSE curriculum portal](https://cbseacademic.nic.in/curriculum_2027.html)

