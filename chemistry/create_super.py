import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Define superuser credentials
SUPERUSER_USERNAME = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
SUPERUSER_EMAIL = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@uindy.edu')
SUPERUSER_PASSWORD = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpass')

# Define required groups
REQUIRED_GROUPS = ['Admin', 'Professors', 'Students']

# Create required groups if they don't exist
for group_name in REQUIRED_GROUPS:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created.")
    else:
        print(f"Group '{group_name}' already exists.")

# Create the superuser if it doesn't exist
if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
    superuser = User.objects.create_superuser(
        username=SUPERUSER_USERNAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD,
    )
    print(f"Superuser {SUPERUSER_USERNAME} created successfully.")
else:
    superuser = User.objects.get(username=SUPERUSER_USERNAME)
    print(f"Superuser {SUPERUSER_USERNAME} already exists.")

# Add the superuser to the Admin group
admin_group = Group.objects.get(name='Admin')
if not superuser.groups.filter(name='Admin').exists():
    superuser.groups.add(admin_group)
    print(f"Superuser {SUPERUSER_USERNAME} added to the 'Admin' group.")
else:
    print(f"Superuser {SUPERUSER_USERNAME} is already in the 'Admin' group.")