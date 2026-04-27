#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata library/fixtures/books.json
echo "
from django.contrib.auth.models import User
import os
u, created = User.objects.get_or_create(username=os.environ['DJANGO_ADMIN_USER'])
u.set_password(os.environ['DJANGO_ADMIN_PASSWORD'])
u.is_staff = True
u.is_superuser = True
u.save()
" | python manage.py shell
python manage.py axes_reset