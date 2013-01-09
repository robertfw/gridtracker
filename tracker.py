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
    '2013-01-07': 'good',
    '2013-01-08': 'good'
}

# data = {
#     '2013-01-01': 'good',
#     '2013-01-02': 'good',
#     '2013-01-03': 'great',
#     '2013-01-04': 'good',
#     '2013-01-05': 'bad',
#     '2013-01-06': 'bad',
#     '2013-01-07': 'terrible'
# }


ratings = {
    'great': 2,
    'good': 1,
    'bad': 0,
    'terrible': -1
}


def rate_week(days, today):
    thresholds = {
        'great': 2 * ratings['great'] + 5 * ratings['good'],
        'good': 7 * ratings['good'],
        'bad': 5 * ratings['good'],
        'terrible': None
    }

    grace_points = sum(day.year != today.year for day in days)

    score = get_score_for_week(days) + grace_points
    for rating, level in thresholds.iteritems():
        if score > level:
            week_status = rating
            break

    return week_status


def get_score_for_week(days):
    return sum(ratings.get(get_status_for_date(day), 0) for day in days)


def get_classes_for_date(date, today):
    statii = []

    if date.year != today.year:
        statii.append('blank')

    if date == today:
        statii.append('today')
    elif date > today:
        statii.append('future')

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

        .future {
            background: #EEE;
        }

        .great {
            background: #FFD700;
        }

        .good {
            background: #33DD77;
        }

        .bad {
            background: #BB4433;
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
            border: 1px dotted blue;
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

        if all(day > today for day in week):
            week_status = 'blank'
        elif any(day > today for day in week):
            week_status = 'pending'

        else:
            week_status = rate_week(week, today)

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
