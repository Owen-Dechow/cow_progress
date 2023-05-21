#!/bin/bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

rm cow_progress/.env
echo "SECRET_KEY='django-insecure'
EMAIL_HOST_USER='host.user@gmail.com'
EMAIL_HOST_PASSWORD='password'" >> cow_progress/.env

python3 manage.py migrate
python3 manage.py flush

python3 manage.py shell << PYTHON

from base.models import Herd
Herd.make_public_herd("Public Herd A", "PHA's", "Star")
Herd.make_public_herd("Public Herd B", "PHB's", "Plus")

PYTHON

echo "
----------------------------------- Setup Complete -----------------------------------

- Virtual environment created.
- Requirements installed.
- Database populated.
- .env file created.

- Remember to set DEBUG to False and set ALLOWED_HOSTS in settings.py file.
- Please update .env file before running.

Thank you,
    Owen Dechow!

--------------------------------------------------------------------------------------
"