# Document Copilot API

From the `backend` directory:

```powershell
Copy-Item .env.example .env  # then add your credentials
uv sync
uv run uvicorn app.main:app --reload
```

The API runs at <http://127.0.0.1:8000>. Check `GET /health` or open the
interactive docs at <http://127.0.0.1:8000/docs>.

```powershell
uv run pytest              # run tests
uv run ruff check app tests
uv add <package>           # add a dependency
uv remove <package>        # remove a dependency
```
