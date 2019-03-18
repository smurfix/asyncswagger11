#!/usr/bin/make -f

all:
	@echo "Please use 'python setup.py'."
	@exit 1

tag:	
	./mktag

pypi:	tag
	python3 setup.py sdist upload
	## version depends on tag, so re-tagging doesn't make sense

upload: pypi
	git push --tags

.PHONY: all tag pypi upload
