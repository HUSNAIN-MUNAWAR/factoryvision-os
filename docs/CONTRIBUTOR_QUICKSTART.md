# Contributor Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
make demo
uvicorn apps.api.main:app --reload
```

For the frontend, run `npm ci`, then `npm run lint`, `npm run typecheck`, `npm test` and `npm run build` inside `apps/web`. In this release environment npm installation timed out, so contributors should run those gates locally or in CI before merging UI changes.
