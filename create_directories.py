import os
from pathlib import Path

# Get the absolute path to the project directory
BASE_DIR = Path(__file__).resolve().parent

print(f"Creating directories in: {BASE_DIR}")

# Create required directories
directories = [
    'static',
    'static/images',
    'static/css',
    'static/js',
    'media',
    'media/assignments',
    'media/course_materials',
    'media/book_covers',
    'staticfiles'
]

for directory in directories:
    dir_path = BASE_DIR / directory
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created/Verified directory: {dir_path}")
    except Exception as e:
        print(f"Error creating directory {dir_path}: {str(e)}")

# Create an empty default cover image if it doesn't exist
default_cover = BASE_DIR / 'static' / 'images' / 'default_cover.jpg'
try:
    if not default_cover.exists():
        print(f"Creating default cover image: {default_cover}")
        default_cover.touch()
        print("Default cover image created successfully")
    else:
        print("Default cover image already exists")
except Exception as e:
    print(f"Error creating default cover image: {str(e)}")

print("\nDirectory creation complete. Please verify the following paths exist:")
for directory in directories:
    path = BASE_DIR / directory
    print(f"{path}: {'Exists' if path.exists() else 'Missing'}")
