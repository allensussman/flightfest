SHELL := $(shell which bash)
ACTIVATE_VENV =  source venv/bin/activate

setup: requirements.txt
	virtualenv venv
	${ACTIVATE_VENV} && pip install -r $<

.PHONY: setup