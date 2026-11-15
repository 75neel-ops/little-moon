# Little Moon — CBSE Classes 1–8

**Little Moon** is an independent Streamlit learning app for CBSE learners in Classes 1–8, created by **NilanjanC**. Students choose a class, subject and suggested chapter, or enter a chapter from their school syllabus. Activities include key words, fresh multiple-choice practice with explanations, custom-mark timed question papers, PDF downloads, and fun facts.

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
3. Deploy the app under its own public URL. Copy that URL to `app-url.txt` in this repository and commit it so the branded install page can open the app.

## Install on desktop or mobile

The PWA page and moon icons are in this repository. Enable GitHub Pages for the `main` branch using the repository root as the source. Open `https://75neel-ops.github.io/little-moon/` and use your browser's **Install app** option. On iPhone or iPad, use **Share → Add to Home Screen**. The icon and installed name are **Little Moon**.

The desktop and mobile install page will use Little Moon's own moon icon and name.

## Student trials and paid access

Little Moon requires a verified student/parent email sign-in. A new account receives one two-day trial. Access and payment entitlements are stored in Supabase so they persist across browser sessions. Razorpay Checkout is enabled through the separate `billing_service` FastAPI service; the existing Razorpay payment button is for donations and is not used to grant student access.

### Setup

1. Create a Supabase project. In **Authentication → Email**, configure the email template to show the one-time code (`{{ .Token }}`), and keep email confirmation enabled.
2. In Supabase SQL Editor, run [`billing_service/schema.sql`](billing_service/schema.sql).
3. Deploy `billing_service` as a Render web service using [`billing_service/render.yaml`](billing_service/render.yaml). Set these environment variables there: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET`. Use the Razorpay **test** API keys first.
4. Add Streamlit app Secrets: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `BILLING_API_URL` (the deployed billing service URL):

   ```toml
   SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
   SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
   BILLING_API_URL = "https://YOUR_RENDER_SERVICE.onrender.com"
   ```

5. Configure Razorpay Dashboard to auto-capture payments. Set live API keys only after the test flow is verified. Never put the Razorpay secret or Supabase service-role key in Streamlit Secrets or browser code; keep them only in the billing service environment.

The default plans are ₹50/15 days, ₹100/30 days, ₹250/90 days, ₹450/180 days, and ₹800/365 days. To change them, set `PLAN_CONFIG_JSON` on the billing service to a JSON array such as:

```json
[{"id":"15-days","label":"15 days","amount_rupees":50,"duration_days":15}]
```

Durations are fixed day counts (three months = 90 days, six months = 180 days, one year = 365 days). A successful payment is signature-checked and confirmed as captured with Razorpay before the service grants access.

## Question freshness

Generated questions use `gemini-3.5-flash-lite`. Repeated wording is filtered within the current browser session and activity. Without shared storage, Little Moon cannot guarantee questions never repeat across different students or later sessions.

## Curriculum references

- [NCERT textbooks and Grades I–VIII catalogue](https://ncert.nic.in/textbook.php)
- [NCERT Bridge Programme](https://ncert.nic.in/bridge_programme.php)
- [CBSE curriculum portal](https://cbseacademic.nic.in/curriculum_2027.html)

