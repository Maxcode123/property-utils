PY_FILES := $(shell find src/property_utils -not -path '*/tests/*' -not -name '__init__.py' -name '*.py')

install-package-builder:
	$(PIP) install --upgrade build

install-package-uploader:
	$(PIP) install --upgrade twine

install-local-package:
	$(PIP) install -e .

test-package:
	$(INTERPRETER) -m unittest discover -v src/property_utils/tests/

doctest-package:
	$(INTERPRETER) -m doctest -v $(PY_FILES)

build-package:
	$(INTERPRETER) -m build

upload-package:
	$(INTERPRETER) -m twine upload --verbose -u '__token__' dist/*

clean:
	rm -rf dist src/property_utils.egg-info