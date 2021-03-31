# DNS Stats
Stats on DNS and email security feature usage

## Setup
You will need python3.6+, pip and virtualenv installed.

1. `git clone git@git.assignitapp.com:dnstats/dnstats.git`
1. `cd dnstats`
1. `virtualenv venv -p python3`
1. `pip install -r requirements.txt`

## Overview
This project uses [Celery](https://docs.celeryproject.org/en/stable/#) and 
the main code for it is located in `dnstats/celery`.
