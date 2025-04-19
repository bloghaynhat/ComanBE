import os
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError

def load_superuser_once():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if not User.objects.filter(is_superuser=True).exists():
        print("⚙️  No superuser found. Loading from fixture...")
        try:
            call_command('loaddata', 'superuser_fixture.json')
            print("✅ Superuser loaded from fixture.")
        except Exception as e:
            print("❌ Error loading superuser fixture:", e)
    else:
        print("✅ Superuser already exists. Skipping fixture load.")
