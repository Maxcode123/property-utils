CONFIG=./pyproject.toml
PY_FILES:=$(shell find src/property_utils -not -path '*/tests/*' -not -name '__init__.py' -name '*.py')

install-package-linter:
	$(PIP) install pylint

install-package-type-checker:
	$(PIP) install mypy

install-package-formatter:
	$(PIP) install black

install-package-builder:
	$(PIP) install --upgrade build

install-package-uploader:
	$(PIP) install --upgrade twine

install-local-package:
	$(PIP) install -e .

install-requirements:
	$(PIP) install typing-extensions

install-test-requirements:
	$(PIP) install unittest-extensions

test-package:
	$(INTERPRETER) -m unittest discover -v src/property_utils/tests/

doctest-package:
	$(INTERPRETER) -m doctest $(PY_FILES)

lint-package:
	$(INTERPRETER) -m pylint --ignore tests --disable C0114,C0301,C0302 src/property_utils

type-check-package:
	$(INTERPRETER) -m mypy --config-file $(CONFIG) ./src/property_utils/

format-package:
	$(INTERPRETER) -m black --config $(CONFIG) ./src/property_utils/

build-package:
	$(INTERPRETER) -m build

upload-package:
	$(INTERPRETER) -m twine upload --verbose -u '__token__' dist/*

clean:
	rm -rf dist src/property_utils.egg-info