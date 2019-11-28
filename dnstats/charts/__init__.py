import subprocess
from jinja2 import Environment, FileSystemLoader

from dnstats.db import db_session, engine
from dnstats.db import models as models


def render_pie(categories, filename: str):
    # This method assumes that there is no file extension
    file_loader = FileSystemLoader('/Users/mburket/code/dnsstats/dnstats/charts/templates')
    env = Environment(loader=file_loader)
    template = env.get_template('pie_charts.tex.j2')
    result = template.render(categories=categories)
    with open('{}.tex'.format(filename), 'w') as f:
        f.write(result)
    subprocess.run(['pdflatex', filename])
    subprocess.run(['magick', 'convert', '-density', '3000', '-scale', 'x740', '{}.pdf'.format(filename),
                    '{}.png'.format(filename)])


def get_categories_from_query(run_id: int, query: str):
    # This method assumes that the count is in column 0, name of the group is in column 1, and color is in column 2
    categories = []
    with engine.connect() as connection:
        total_count = db_session.query(models.SiteRun).filter_by(run_id=run_id).count()
        result_set = connection.execute(query)

        for row in result_set:
            category = {'percent': round((row[0]/total_count) * 100, 1), 'name': row[1], 'color': row[2]}
            categories.append(category)
    return categories

