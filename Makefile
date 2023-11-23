PACKAGE_NAME := aws_nuke_exporter
TEST_PYPI_REPO := https://test.pypi.org/legacy/
PYPI_REPO := https://upload.pypi.org/legacy/

.PHONY: build check-twine upload-test upload

setup:
	pip install wheel twine --user

build: setup

build:
	python setup.py sdist bdist_wheel

check-twine:
	@command -v twine > /dev/null 2>&1 || pip install twine --user

upload-test: build check-twine
	twine upload -r testpypi_nuke dist/*

upload: build check-twine
	twine upload -r pypi_nuke dist/*

clean:
	rm -rf dist build $(PACKAGE_NAME).egg-info
