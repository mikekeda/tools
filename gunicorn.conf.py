"""
Gunicorn config.
"""
bind = "unix:/uwsgi/tools.sock"
workers = 2
timeout = 30
max_requests = 100
daemon = False
umask = "91"
user = "nginx"
loglevel = "info"
