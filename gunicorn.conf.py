"""
Gunicorn config.
"""
bind = 'unix:/home/voron/socks/tools.sock'
workers = 2
timeout = 30
max_requests = 100
daemon = False
umask = '91'
loglevel = 'info'
