test:
	pip install -r requirements-tests.txt
	nosetests
	flake8 rest_api_framework
