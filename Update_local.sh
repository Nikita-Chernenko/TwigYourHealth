#!/usr/bin/env bash
C:\\.virtualenv\\TwigYourHealth\\Scripts\\activate
git pull origin master
pip install -r requirements.txt
python manage.py reset_staging --settings="TwigYourHealth.base_settings"