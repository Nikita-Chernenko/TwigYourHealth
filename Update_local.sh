git pull origin master
pip install -r requirements.txt
python manage.py reset_staging
python manage.py runserver