css :
	stylus -w -c www/index.styl

isort :
	isort -rc -y lib

black :
	black -S -l 78 lib

unify :
	unify -r --quote="'" lib

flake8 :
	flake8 lib

zbs : isort black unify flake8

parse:
	python -m lib.cli parse

render:
	python -m lib.cli render

all:
	python -m lib.cli all

serve:
	uvicorn lib.app:app --host 0.0.0.0 --port 80
