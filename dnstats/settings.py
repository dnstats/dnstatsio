AMQP = 'amqp://guest@localhost/'
DB = 'postgres://dnstats@localhost/dnstats'
CELERY_BACKEND = 'db+postgresql://dnstats@localhost/dnstats'
DNSTATS_ENV = 'Development'
UPLOAD_REPORTS = False
USE_SENTRY = False

# Reports
REPORT_S3_URL_BASE = ''
REPORT_S3_ACCESS_KEY = ''
REPORT_S3_SECRET_KEY = ''
REPORT_S3_BUCKET_NAME = ''
REPORT_S3_REGION = ''

try:
    from dnstats.settingslocal import *
except ImportError:
    print("Local settings not found")
