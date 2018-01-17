#!/usr/bin/make -f

all:
	@echo "Please use 'python setup.py'."
	@exit 1

pypi:
	@if python3 setup.py -V 2>/dev/null | grep -qs + >/dev/null 2>&1 ; \
		then echo "You need a clean, tagged tree" >&2; exit 1 ; fi
	python3 setup.py sdist upload
	## version depends on tag, so re-tagging doesn't make sense
	#git tag v ..shell python3 setup.py -V.

upload: pypi
	git push-all --tags
