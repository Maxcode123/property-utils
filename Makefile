
install-package-builder:
	$(PIP) install --upgrade build

install-package-uploader:
	$(PIP) install --upgrade twine

install-local-package:
	$(PIP) install -e .

test-package:
	$(INTERPRETER) -m unittest discover -v src/property_utils/tests/

build-package:
	$(INTERPRETER) -m build

upload-package:
	$(INTERPRETER) -m twine upload --verbose -u '__token__' dist/*

clean:
	rm -rf dist src/property_utils.egg-info