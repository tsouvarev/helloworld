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

browse:
	python -m lib.cli browse

serve: browse css

cron: parse render browse
	git commit -a -m "Update www/data.js" && git push
