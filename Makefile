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
	python -m lib.cmd parse

render:
	python -m lib.cmd render
