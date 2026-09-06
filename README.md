# 📚 Study Scheduler

A full-stack study-planning app for CA/commerce students. Schedule subjects,
units and daily tasks on a calendar; track subject-wise progress; get
Pomodoro/study reminders; and let the app **recalculate your daily workload
and burden index** when you skip tasks.

- **Frontend:** React (Vite) + TailwindCSS → GitHub Pages
- **Backend:** FastAPI + SQLAlchemy → Render (or Heroku) free tier
- **Database:** PostgreSQL

```
study-scheduler/
├── backend/          FastAPI app, models, routers, seed data
│   └── app/
├── frontend/         React + Tailwind (Vite) SPA
│   └── src/
└── .github/workflows/deploy-frontend.yml   (optional CI for Pages)
```

---

## Features

| Requirement | Where |
|---|---|
| Calendar to schedule subjects/units/tasks | `frontend/src/components/Calendar.jsx` |
| Progress dashboard (subject-wise %) | `Dashboard.jsx` + `GET /progress` |
| Reminder settings (Pomodoro, alerts) | `Reminders.jsx` |
| Adaptive workload + burden index | `Workload.jsx` + `GET /progress/workload/all` |
| Simple username/password login | `Login.jsx` + `/auth/*` (JWT) |
| CRUD Subjects/Units/Tasks | `backend/app/routers/*` |
| Mark complete → auto-update progress | `POST /tasks/{id}/complete` |
| Skip → recalculate hours/burden | `POST /tasks/{id}/skip` |
| Reminder scheduling / next times | `GET /reminders/next` |
| Seed data for 5 subjects | `backend/app/seed.py` |

---

## Database schema

| Table | Columns |
|---|---|
| `subjects` | id, name, total_units, total_hours |
| `units` | id, subject_id, name, planned_hours, completed_hours |
| `tasks` | id, unit_id, date, planned_hours, completed_hours, status |
| `progress_logs` | id, subject_id, date, completion_percent |
| `reminders` | id, task_id, reminder_time, status |
| `users` | id, username, hashed_password (for login) |

Tables are created automatically on backend startup (`Base.metadata.create_all`).

---

## Run locally

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate      |  macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then edit DATABASE_URL + SECRET_KEY
```

Make sure PostgreSQL is running and the database exists:

```bash
createdb study_scheduler        # or use pgAdmin / psql
```

Seed the 5 subjects + demo user (`student` / `password123`):

```bash
python -m app.seed
```

Start the API (docs at http://localhost:8000/docs):

```bash
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env       # VITE_API_URL=http://localhost:8000
npm run dev                # http://localhost:5173
```

Log in with **student / password123**.

---

## Deploy the backend to Render (free)

1. Push this repo to GitHub.
2. On [render.com](https://render.com) → **New +** → **Blueprint**, and select
   your repo. Render reads `backend/render.yaml` and provisions:
   - a **PostgreSQL** instance (`study-scheduler-db`), and
   - a **web service** (`study-scheduler-api`) with `DATABASE_URL` wired in and
     a random `SECRET_KEY` generated.
3. After the first deploy, set the **`CORS_ORIGINS`** env var on the web service
   to your GitHub Pages URL, e.g. `https://<username>.github.io` → **Save**
   (this triggers a redeploy).
4. Seed the deployed DB once — open the service **Shell** tab and run:
   ```bash
   python -m app.seed
   ```
5. Your API base URL is `https://study-scheduler-api.onrender.com`.

> **Heroku alternative:** `heroku create`, add the **Heroku Postgres** add-on
> (sets `DATABASE_URL`), `heroku config:set SECRET_KEY=... CORS_ORIGINS=...`,
> then `git push heroku main`. The included `Procfile` runs uvicorn. Seed with
> `heroku run python -m app.seed`.

---

## Deploy the frontend to GitHub Pages

`vite.config.js` sets `base: "/study-scheduler/"` — change it if your repo has a
different name. The app uses `HashRouter`, so routes work on Pages with no
extra config.

### Option A — one command (gh-pages branch)

```bash
cd frontend
# Point the build at your deployed API:
echo "VITE_API_URL=https://study-scheduler-api.onrender.com" > .env
npm install
npm run build
npm run deploy        # publishes ./dist to the gh-pages branch
```

Then in GitHub: **Settings → Pages → Source = "Deploy from a branch" →
`gh-pages` / root**. Site goes live at
`https://<username>.github.io/study-scheduler/`.

### Option B — GitHub Actions (auto-deploy on push)

`.github/workflows/deploy-frontend.yml` builds and deploys on every push to
`main`.

1. **Settings → Pages → Source = "GitHub Actions"**.
2. **Settings → Secrets and variables → Actions → Variables** → add
   `VITE_API_URL = https://study-scheduler-api.onrender.com`.
3. Push to `main`.

---

## Connecting the two

The frontend talks to the backend purely over REST using `VITE_API_URL`.
Ensure the backend's `CORS_ORIGINS` includes your Pages origin
(`https://<username>.github.io`) or requests will be blocked by the browser.

---

## Adaptive workload — how the burden index works

For each subject the backend (`app/services.py`) computes:

- `remaining_hours` = planned − completed hours
- `remaining_days`  = days until the last scheduled task
- `original_daily_hours` = planned hours spread evenly over the whole schedule
- `recommended_daily_hours` = remaining_hours ÷ remaining_days
- **`burden_index` = recommended ÷ original**

A burden index of `1.0` means you're on plan; `1.5×` means skipped tasks have
pushed your required daily study 50% above the original plan. The Workload
page colour-codes this as *On track / Slightly behind / Overloaded*.
