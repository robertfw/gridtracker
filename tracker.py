from wsgiref.simple_server import make_server
import datetime
import calendar


data = {
    '2013-01-01': 'good',
    '2013-01-02': 'good',
    '2013-01-03': 'good',
    '2013-01-04': 'good',
    '2013-01-05': 'bad',
    '2013-01-06': 'bad',
    '2013-01-07': 'good'
}


def get_classes_for_date(date, today):
    statii = []

    if date.year != today.year:
        statii.append('blank')

    if date == today:
        statii.append('today')

    status = get_status_for_date(date)
    if status:
        statii.append(status)
    else:
        statii.append('nodata')

    return ' '.join(statii)


def get_status_for_date(date):
    day_key = date.strftime('%Y-%m-%d')
    return data.get(day_key, None)


def application(env, start_response):
    content = '''
    <html>
    <head>
    <style type="text/css">
        ul.calender-grid {
            width: 520px;
            padding: 0px;
            margin: 0px;
        }
        ul.calendar-grid .week {
            display: inline;
            list-style-type: none;
            float: left;
        }

        ul.calendar-grid .week ul {
            padding: 0px;
        }

        .square  {
            border: 1px solid white;
            display: list-item;
            width: 10px;
            height: 10px;
            list-style-type: none;
        }

        .nodata {
            background: #CCC;
        }

        .great {
            background: #FFD700;
        }

        .good {
            background: #00DD00;
        }

        .bad {
            background: #AA0000;
        }

        .terrible {
            background: #000;
        }

        .blank {
            background: none;
        }

        .today {
            border: 1px dotted blue;
        }

        .week-summary {
            margin-top: 10px;
        }

        .week-summary.pending {
            border: 1px dotted lightblue;
        }
    </style>
    </head>
    <body>
    '''

    today = datetime.date.today()

    cal = calendar.Calendar(6)

    days = [day
            for month in range(1, 13)
            for day in cal.itermonthdates(today.year, month)]

    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]

    content += '<ul class="calendar-grid">'
    for week in weeks:
        content += '<li class="week"><ul>'

        for day in week:
            content += '<li class="square {classes}"></li>'.format(week=week, day=day, classes=get_classes_for_date(day, today))

        week_status = 'pending'
        content += '<li class="square week-summary {week_status}"></li>'.format(week_status=week_status)

        content += '</ul></li>'

    content += '</ul>'

    content += '''
    </body>
    </html>
    '''

    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)

    return [content]


if __name__ == '__main__':

    httpd = make_server('', 8000, application)
    httpd.serve_forever()
