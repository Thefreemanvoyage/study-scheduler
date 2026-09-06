# Deploy Study Scheduler to Vercel (all-in-one)

This hosts **everything on Vercel**: the React frontend as static files and the
FastAPI backend as a Python serverless function under `/api`, backed by a free
**Neon PostgreSQL** database. One domain, no CORS.

```
study-scheduler/          # repo root = the Vite React app (Vercel auto-detects it)
├── index.html, src/, public/, package.json, vite.config.js, ...
├── vercel.json           # routing: /api/* -> serverless function
├── requirements.txt      # Python deps for the serverless function
├── api/index.py          # serverless entry (mounts FastAPI under /api)
└── backend/app/...        # the FastAPI app (imported by api/index.py)
```

## Step 1 — Put the code on GitHub

From `study-scheduler/` (already a git repo with a first commit):

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/study-scheduler.git
git push -u origin main
```

(Create the empty `study-scheduler` repo first at https://github.com/new — no
README/gitignore, since this repo already has them.)

## Step 2 — Create a free PostgreSQL database (Neon)

1. Go to https://neon.tech → sign up (free tier) → **Create project**.
2. Copy the **connection string** — it looks like:
   `postgresql://user:pass@ep-xxxx.aws.neon.tech/neondb?sslmode=require`
3. Keep it handy for Step 3.

> Alternative: Vercel's own Postgres (Storage tab) or Supabase — any Postgres
> URL works. Use the **pooled** connection string if offered (better for
> serverless).

## Step 3 — Import the project into Vercel

1. Go to https://vercel.com → **Add New → Project** → import your GitHub repo.
2. Vercel auto-detects `vercel.json`. Leave the build settings as-is.
3. Before deploying, open **Environment Variables** and add:

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | your Neon connection string from Step 2 |
   | `SECRET_KEY` | any long random string (e.g. run `python -c "import secrets;print(secrets.token_hex(32))"`) |
   | `SEED_TOKEN` | any secret word you choose (used once, next step) |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |

4. Click **Deploy**. You'll get a URL like `https://study-scheduler-xxxx.vercel.app`.

## Step 4 — Seed the database (once)

Tables are created automatically on first request. To load the demo user + 5
subjects, call the guarded seed endpoint once (replace the token with your
`SEED_TOKEN`):

```bash
curl -X POST "https://<your-app>.vercel.app/api/admin/seed?token=YOUR_SEED_TOKEN"
```

Expected: `{"status":"seeded","login":"student / password123"}`
(Calling it again returns `already_seeded` — it never overwrites data.)

## Step 5 — Use it

Open `https://<your-app>.vercel.app` and log in with **student / password123**
(or click **Register** to create your own account).

## Verify the API directly (optional)

- Health:   `https://<your-app>.vercel.app/api/`
- Docs:     `https://<your-app>.vercel.app/api/docs`

## Notes / troubleshooting

- **`DATABASE_URL` is required.** Without it the backend tries SQLite, which
  can't be written on Vercel's read-only filesystem. Set it to your Neon URL.
- **Redeploys:** every `git push` to `main` triggers a new Vercel deployment.
- **Env var changes** require a redeploy to take effect (Vercel → Deployments →
  Redeploy).
- **Security:** once seeded, you can remove the seed endpoint — delete
  `backend/app/routers/admin.py`, its two lines in `backend/app/main.py`, and
  redeploy. Leaving it is safe as long as `SEED_TOKEN` stays secret.
- **Cold starts:** the free serverless tier sleeps; the first request after idle
  takes a second or two. Normal.
