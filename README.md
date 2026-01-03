# eMoney Platform – Projet L3 IFNTI

Plateforme de transfert d’argent électronique conforme au cahier des charges.

## Fonctionnalités
- Inscription + OTP (2 min)
- Retrait avec OTP (3 min)
- Dépôt, transfert, retrait
- Frais de 2 % sur retrait → 2 transactions (`withdrawal` + `fee`)
- Suspension par admin
- Soldes recalculables depuis les transactions
- Journalisation (`logs/server.log`)

## Technologies
- Django 4.2.15 (compatible Python 3.8)
- PostgreSQL
- Tailwind CSS (via CDN)
- Docker

## Installation
```bash
git clone ...
cd e-money-platform
p3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Créer logs
mkdir logs

# DB init
p3 manage.py makemigrations
p3 manage.py migrate

# Créer compte plateforme
p3 manage.py shell
>>> from accounts.models import User, VirtualAccount
>>> u = User.objects.create_user(username='platform', email='platform@emoney.tg', password='platform')
>>> VirtualAccount.objects.create(user=u)
>>> exit()

p3 manage.py createsuperuser
p3 manage.py runserver
# e-money_plateform
Plateforme de retrais d'argent
