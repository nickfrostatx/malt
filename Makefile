test:
	py.test -vv --pep8 --pep257 --cov=malt --cov-report=term-missing malt tests

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
