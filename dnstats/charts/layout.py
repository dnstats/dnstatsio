def chart(id: str):
    return '<div class="chart" id="{}"></div>'.format(id)


def row(*args):
    if len(args) != 2:
        raise ValueError("Must be two items")
    out = '<div class="section group">'

    columns = len(*args)

    for column in range(columns-1):
        column_number = column + 1
        out += '<div class="col span_{}_of_{}">'
        out += args[column]
        out += '</div>'
