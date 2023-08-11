# Instructions for Notifications-admin

This file contains all the instructions required to run the `admin` locally.

## Prerequisites

* Python 3.9 (at the moment of writing the instructions don't cover running the app locally in Docker)
* Nodejs 16.14.0

## Running app

1. In the root of the app create `environment.sh` with the following content
```
export NOTIFY_ENVIRONMENT='development'
export FLASK_APP=application.py
export FLASK_DEBUG=1
export WERKZEUG_DEBUG_PIN=off
```
1. Run `$ make bootstrap` to install all the dependencies
1. Run `$ make run-flask` to run the app
1. The app is now available at `localhost:6012`
1. To start using the app, create an account
