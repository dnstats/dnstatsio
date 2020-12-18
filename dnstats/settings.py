AMQP = 'amqp://guest@localhost/'
DB = 'postgres://dnstats@localhost/dnstats'
CELERY_BACKEND = 'db+postgresql://dnstats@localhost/dnstats'
DNSTATS_ENV = 'Development'
UPLOAD_REPORTS = False


try:
    from dnstats.settingslocal import *
except ImportError:
    print("Local settings not found")
