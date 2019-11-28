import subprocess

from jinja2 import Environment, FileSystemLoader


def render_pie(categories, filename: str):
    file_loader = FileSystemLoader('/Users/mburket/code/dnsstats/dnstats/charts/templates')
    env = Environment(loader=file_loader)
    template = env.get_template('pie_charts.tex.j2')
    result = template.render(categories=categories)
    with open(filename, 'w') as f:
        f.write(result)
    subprocess.run(['pdflatex', filename])
    subprocess.run(['magick', 'convert', '-density', '3000', '-scale', 'x740', filename.replace('.tex', '.pdf'),
                    filename.replace('.tex', '.png')])
