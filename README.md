Tools
======================

This is site where you can use different tools.

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
