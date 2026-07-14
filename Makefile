.PHONY: demo test api web lint clean
demo:
	python -m factoryvision.cli demo
	python scripts/render_demo_assets.py
test:
	pytest
api:
	uvicorn apps.api.main:app --reload
web:
	npm --prefix apps/web run dev
lint:
	ruff check factoryvision tests
clean:
	rm -rf artifacts factoryvision.db .pytest_cache

.PHONY: phase2-test sbom release-validate
phase2-test:
	pytest -q
	python -m compileall -q factoryvision
sbom:
	python -c "import json,importlib.metadata as m; from pathlib import Path; Path('artifacts/sbom').mkdir(parents=True,exist_ok=True); Path('artifacts/sbom/python-inventory.json').write_text(json.dumps(sorted([{'name':d.metadata.get('Name'),'version':d.version} for d in m.distributions() if d.metadata.get('Name')],key=lambda x:x['name'].lower()),indent=2))"
release-validate:
	python scripts/validate_release.py
