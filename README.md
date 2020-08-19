Tools
======================

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b6e6d3bc93504b86bef179a500978a19)](https://app.codacy.com/manual/mikekeda/tools?utm_source=github.com&utm_medium=referral&utm_content=mikekeda/tools&utm_campaign=Badge_Grade_Settings)

This is site where you can use different tools.
Link to the site - https://tools.mkeda.me

Tools description (available without registration)
------------
- **Canvas** - Online canvas image drawing tool.
- **Image to base64** - Covert image to base64 format.
- **Exif info** - Get exif info from image with geolocation data.
- **Text manipulation** - Capitalize text, convert text to lowercase or uppercase. Count amount of letters in the text.
- **Unit convector** - Convert units for temperature, distance, volume, area, mass.

Tools description (registration is needed)
------------
- **Calendar** - Add events to your Calendar and get email notifications about upcoming events.
- **Dictionary** - Online dictionary.
- **Flashcards** - Add flashcards to memorize something.
- **Task Board** - Task Board where you can manage your tasks.
- **Code snippets** - Instantly share code, notes, and snippets.
- **Read it later** - Save links to read it later.

Installation
------------
    # Install Redis
    sudo apt install redis-server
    # Install postgresql
    sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.6
    # Configure database
    sudo su - postgres
    psql
    CREATE USER tools_admin WITH PASSWORD 'home_pass';
    CREATE DATABASE tools;
    GRANT ALL PRIVILEGES ON DATABASE tools to tools_admin;
    # Install packages
    pip install -r requirements.txt
    # Apply migrations
    python manage.py migrate
    # Create an admin user
    python manage.py createsuperuser

Running
-------
    # Locally
    python manage.py runserver

Upgrade python packages
-------
    # Remove versions from requirements.txt
    # Upgrade python packages
    pip install --upgrade --force-reinstall -r requirements.txt
    # Update requirements.txt
    pip freeze > requirements.txt

Useful manage.py commands
-------
    # Run tests
    python manage.py test
    # Run tests and check code style and coverage
    python manage.py jenkins --enable-coverage --pep8-exclude migrations --pylint-rcfile .pylintrc
    # Clearing Silk logged data
    python manage.py silk_clear_request_log
