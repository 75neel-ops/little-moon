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

## Student trials and manual payment approval

Students sign in with a verified email code and receive a two-day trial. After it expires, Little Moon shows the plan prices and Razorpay payment button. Payment checks and access activation are manual: students send their Little Moon email and Razorpay payment ID/receipt to the teacher/app owner. The app tells them approval may take some time and asks them not to pay twice while waiting. The owner checks the payment in Razorpay, then grants the matching plan from **Owner: approve a payment** in the sidebar.

### Setup

1. Create a Supabase project. In **Authentication → Email**, configure the email template to show the one-time code (`{{ .Token }}`), and keep email confirmation enabled.
2. In Supabase SQL Editor, run [`supabase_schema.sql`](supabase_schema.sql).
3. In Streamlit Community Cloud, add these app Secrets. `SUPABASE_SERVICE_ROLE_KEY` and `ADMIN_PASSWORD` stay server-side and are never sent to students:

   ```toml
   SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
   SUPABASE_PUBLISHABLE_KEY = "YOUR_SB_PUBLISHABLE_KEY"
   SUPABASE_SECRET_KEY = "YOUR_SB_SECRET_KEY"
   ADMIN_PASSWORD = "CHOOSE_A_LONG_RANDOM_OWNER_PASSWORD"
   RAZORPAY_PAYMENT_BUTTON_ID = "pl_U0PbKCBYERvpCA"
   ```

The Razorpay Custom Payment Button shown in the app contains all five plan items, so a single button ID is enough. The default plan prices are ₹50/15 days, ₹100/30 days, ₹250/90 days, ₹450/180 days, and ₹800/365 days. If you change the prices, update the button's items in Razorpay and set `PLAN_CONFIG_JSON` in Streamlit Secrets to a JSON list with `id`, `label`, `amount_rupees`, and `duration_days` fields so the owner approval form grants the matching duration.

Before paying, students must check that Razorpay displays the same amount as their selected plan. A single fixed-amount button may require you to create separate buttons for the different prices. Until the Supabase settings and owner password are added, the app stays open and displays a setup notice.

## Question freshness

Generated questions use `gemini-3.5-flash-lite`. Repeated wording is filtered within the current browser session and activity. Without shared storage, Little Moon cannot guarantee questions never repeat across different students or later sessions.

## Curriculum references

- [NCERT textbooks and Grades I–VIII catalogue](https://ncert.nic.in/textbook.php)
- [NCERT Bridge Programme](https://ncert.nic.in/bridge_programme.php)
- [CBSE curriculum portal](https://cbseacademic.nic.in/curriculum_2027.html)

