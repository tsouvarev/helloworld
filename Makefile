css:
	stylus -w -c www/index.styl

isort:
	isort -rc -y lib tests

black:
	black -S -l 78 lib tests

unify:
	unify -r --quote="'" lib tests

flake8:
	flake8 lib tests

fmt: isort black unify

test: flake8
	PYTHONPATH="$(PYTHONPATH):$(PWD)" pytest tests

parse:
	python -m lib.cli parse

render:
	python -m lib.cli render

serve:
	uvicorn lib.app:app --host 0.0.0.0 --port 80

cron: parse render
	git commit -a -m "Update www/data.js" && git push
