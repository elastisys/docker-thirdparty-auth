PACKAGE = authserver

# virtual environment to create
VIRTUALENV = venv.$(PACKAGE)

venv:
	virtualenv $(VIRTUALENV)

init: 
	pip install -r requirements.txt

clean:
	find -name '*~' -exec rm {} \;
	find -name '*.pyc' -exec rm {} \;
