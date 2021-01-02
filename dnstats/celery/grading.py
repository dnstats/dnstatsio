from db import db_session, models as models


def _grade_errors(errors: list, grade_type: str, site_run_id: int):
    remark_type = db_session.query(models.RemarkType).filter_by(name=grade_type).one()
    for error in errors:
        remark = db_session.query(models.Remark).filter_by(remark_type_id=remark_type.id, enum_value=error.value).one()
        remark_siterun = models.SiterunRemark(site_run_id=site_run_id, remark_id=remark.id)
        db_session.add(remark_siterun)
        db_session.commit()


def get_site_and_site_run(site_run_id):
    site_run = db_session.query(models.SiteRun).filter(models.SiteRun.id == site_run_id).one()
    site = db_session.query(models.Site).filter(models.Site.id == site_run.site_id).one()
    return site, site_run
