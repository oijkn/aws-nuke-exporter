PACKAGE_NAME := aws_nuke_exporter
TEST_PYPI_INDEX := https://test.pypi.org/simple/
TEST_PYPI_REPO := testpypi_nuke
PYPI_REPO := pypi_nuke
VERSION := $(shell grep -Po "__version__ = \"\K[^\"]+" $(PACKAGE_NAME)/__init__.py)

.PHONY: build check-twine upload-test upload clean install-test

setup:
	pip install wheel twine --user

build: setup
	python setup.py sdist bdist_wheel

check-twine:
	@command -v twine > /dev/null 2>&1 || pip install twine --user

upload-test: build check-twine
	twine upload -r $(TEST_PYPI_REPO) dist/*$(VERSION)*

upload: build check-twine
	twine upload -r $(PYPI_REPO) dist/*$(VERSION)*

install-test:
	pip install -i $(TEST_PYPI_INDEX) --upgrade $(PACKAGE_NAME)

install:
	pip install --upgrade $(PACKAGE_NAME)

clean:
	rm -rf dist build $(PACKAGE_NAME).egg-info

