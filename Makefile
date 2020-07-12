css:
	stylus -w -c docs/index.styl

isort:
	isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=78 lib tests

black:
	black -S -l 78 lib tests

unify:
	unify -r --quote="'" lib tests

flake8:
	flake8 lib tests

fmt: isort black unify

lint:
	mypy --ignore-missing-imports lib tests

test: fmt flake8 lint
	PYTHONPATH="$(PYTHONPATH):$(PWD)" pytest --cov-report=term-missing --cov=lib tests

parse:
	python -m lib.cli parse

render:
	python -m lib.cli render

browse:
	python -m lib.cli browse

serve:
	uvicorn lib.app:app --host 0.0.0.0 --port 80

cron: parse render browse
	git commit -a -m "Update docs/data.js" && git push
