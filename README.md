![Logo](https://eduquiz.win/static/eduquiz/img/logo.png)

[![buildstatus](https://travis-ci.org/ecuatox/eduquiz.svg?branch=master)](https://travis-ci.org/ecuatox/eduquiz)
[![codecov](https://codecov.io/gh/ecuatox/eduquiz/branch/master/graph/badge.svg)](https://codecov.io/gh/ecuatox/eduquiz)
[![website](https://img.shields.io/badge/website-eduquiz.win-blue.svg)](https://eduquiz.win/)

## Local setup
1. Create a virtual environment `virtualenv -p python3 env`
2. Source the environment `source env/bin/activate`
3. Clone the github repository `git clone https://github.com/tenstad/eduquiz.git`
4. Enter the repository `cd eduquiz`
5. Install requirements `pip install -r requirements.txt`
6. Make migrations `python manage.py makemigrations` and `python manage.py makemigrations quiz`
7. Migrate `python manage.py migrate`
8. Run `python manage.py runserver`

## TDT4140 - Software Engineering
EDUQUIZ was created in Pekka Abrahamsson's software engineering cource at NTNU in 2017.

## Team members
* Adrian Hatletvedt
* Ludvig Pedersen
* Vetle Birkeland
* Amund Tenstad
