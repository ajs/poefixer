init:
	pip install -r requirements.txt

test:
	PYTHONPATH=. py.test tests

.PHONY: init test

