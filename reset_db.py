#!/usr/bin/env python3
import os
import sys

# Add the HorizonRealityBackend to the Python path
sys.path.insert(0, '/Users/tejas/Downloads/hr-master/HorizonRealityBackend')
os.chdir('/Users/tejas/Downloads/hr-master/HorizonRealityBackend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HorizonRealityBackend.settings')

import django
django.setup()

from django.core.management import call_command

# Delete the database
db_path = '/Users/tejas/Downloads/hr-master/HorizonRealityBackend/db.sqlite3'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Deleted database: {db_path}")

# Delete all migration files except __init__.py
migrations_dirs = [
    '/Users/tejas/Downloads/hr-master/HorizonRealityBackend/services/migrations',
    '/Users/tejas/Downloads/hr-master/HorizonRealityBackend/home/migrations',
    '/Users/tejas/Downloads/hr-master/HorizonRealityBackend/users/migrations',
    '/Users/tejas/Downloads/hr-master/HorizonRealityBackend/blogs/migrations'
]

for dir_path in migrations_dirs:
    for filename in os.listdir(dir_path):
        if filename.startswith('000') and filename.endswith('.py'):
            filepath = os.path.join(dir_path, filename)
            os.remove(filepath)
            print(f"✓ Deleted migration: {filepath}")

# Run makemigrations
print("\n→ Creating migrations...")
call_command('makemigrations')

# Run migrate
print("\n→ Applying migrations...")
call_command('migrate')

print("\n✓ Database reset complete!")
print("→ You can now run: python manage.py runserver")
