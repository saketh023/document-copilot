# Supabase setup

We use Supabase for **Postgres** (users, chats, source documents, chunks, embeddings, and citations) and **Auth** (email sign-in only). You need one hosted Supabase project before wiring up `backend/` and `frontend/`.

## 1. Create an account

1. Go to [supabase.com](https://supabase.com) and sign up (GitHub or email).
2. Confirm your email if prompted.
3. You land in the [dashboard](https://supabase.com/dashboard). The free tier is enough for local development.

## 2. Create a project

1. Open [New project](https://supabase.com/dashboard/new).
2. Pick your organization (a personal org is created automatically on first signup).
3. Set a **project name** (e.g. `Document Copilot`).
4. Choose a **database password** — save it somewhere safe; you need it for direct DB access and `supabase link`.
5. Pick a **region** close to you.
6. Click **Create new project** and wait until status is healthy (~1–2 minutes).

## 3. Collect credentials

You need these values in backend and frontend env config (exact variable names will live in each service's settings module once the app is built).

| Value | Where to find it | Used by |
| ----- | ---------------- | ------- |
| **Project URL** | Dashboard → **Project Settings** → **API** → Project URL | Frontend + backend |
| **anon (public) key** | Same page → `anon` `public` key | Frontend (browser-safe) |
| **service_role (secret) key** | Same page → `service_role` `secret` key | Backend only — never expose to the browser |
| **Project ref** | Dashboard URL `supabase.com/dashboard/project/<ref>` or `supabase projects list` | CLI commands |
| **Direct database connection string** | Dashboard → **Project Settings** → **Database** → Connection string | Alembic migrations and backend DB access |
| **Database password** | What you set at project creation | Direct Postgres connection |

From the CLI you can also print API keys:

```bash
supabase projects api-keys --project-ref <your-project-ref>
```

Keep `service_role` out of git, client bundles, and frontend env files.

## 4. Auth settings (email only)

This app uses email auth only — no Google/SSO.

1. Dashboard → **Authentication** → **Sign In / Providers**: enable **Email** and allow new users to sign up. No social providers are needed.
2. Set the minimum password length to at least **8** characters to match the signup form. Supabase enforces any additional password rules configured for the project.
3. Under **Authentication → URL Configuration**, set **Site URL** to `http://localhost:5173` and add `http://localhost:5173/login` to **Redirect URLs**. The app sends confirmation links back to `/login`; the Supabase browser client restores the session and the app opens `/app`.
4. Choose your confirmation behavior:
   - Keep **Confirm email** enabled to test the complete inbox confirmation flow. The signup form shows a confirmation notice while no session exists.
   - For local development only, disabling **Confirm email** lets signup sign the user in immediately. Re-enable it before production.
5. For email delivery, Supabase's default SMTP service sends only to addresses belonging to your Supabase organization team and has tight rate limits. Configure **custom SMTP** before testing confirmation with other email addresses or inviting pilot users.
6. Keep the default confirmation email template using `{{ .ConfirmationURL }}`. This SPA uses the browser client's default confirmation flow; it does not implement a server-side `/auth/confirm` endpoint.

References: [password auth](https://supabase.com/docs/guides/auth/passwords), [redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls), [SMTP setup](https://supabase.com/docs/guides/auth/auth-smtp).

### Local signup walkthrough

1. Confirm `frontend/.env` contains the project URL and public anon key for the same Supabase project as the backend. `VITE_API_BASE_URL` should be `http://localhost:8000`. Restart Vite after editing env values.
2. From `backend/`, run `uv run alembic upgrade head`. Migration `20261110_0002` creates a trigger that inserts the matching `public.users` row on signup and backfills existing Auth accounts. Apply this through Alembic, not by pasting schema changes into the dashboard. A failed trigger can block signup, so check Auth logs if signup reports a database error.
3. From `frontend/`, run `pnpm dev --port 5173 --strictPort` and open `http://localhost:5173/signup`.
4. Create an account with an email you control. If confirmation is enabled, follow the confirmation email link. Otherwise, you should reach `/app` immediately.
5. Check **Authentication → Users** for the account, and the Table Editor for a matching `public.users.id`. Refresh `/app` to check session restoration. Sign out, then open `/app` again; it should redirect to `/login`. Sign in with the same email and password.

Signup and sign-in call Supabase Auth directly. The workspace also calls FastAPI's `GET /auth/me` through the shared API client to verify the bearer token and matching application-user row. Start FastAPI with `uv run uvicorn app.main:app --reload` from `backend/`. The workspace should show "Your account is verified and ready". A connection error means the backend could not be reached; incomplete account setup means the application-user row is missing.

The migration is included in the repo; it is not applied automatically when the frontend starts. See [Supabase's user-data trigger guidance](https://supabase.com/docs/guides/auth/managing-user-data).

## 5. Database schema management

Document Copilot uses Alembic from the Python backend to manage database schema. Do not create production tables manually in the Supabase dashboard.

Alembic migrations create and update:

- the `vector` extension for `pgvector`
- source document and chunk tables
- embedding columns
- generated full-text search columns
- HNSW and GIN indexes
- chat and citation tables
- row-level security policies

Use the direct/session database connection string for Alembic. Do not use the transaction pooler connection string for migrations.

From `backend/`:

```bash
uv run alembic upgrade head
```

See [Backend setup](backend-setup.md) for the Alembic workflow.

## Next steps

- [Backend setup](backend-setup.md) — Python service + Supabase client
- [Frontend setup](frontend-setup.md) — React app + `@supabase/supabase-js`
