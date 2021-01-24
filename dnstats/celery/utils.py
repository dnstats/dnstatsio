import settings


def _send_message(email):
    if settings.DNSTATS_ENV == 'Development':
        print(email)
        return


def setup_sentry():
    if settings.DNSTATS_ENV == 'Production' and settings.USE_SENTRY:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.tornado import TornadoIntegration
        sentry_sdk.init(settings.SENTRY,
                        integrations=[CeleryIntegration(), SqlalchemyIntegration(), TornadoIntegration()])