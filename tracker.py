import datetime
import calendar
import pystache


def chunk_list(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]

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

ratings = {
    'great': 2,
    'good': 1,
    'bad': 0,
    'terrible': -1
}

thresholds = {
    'great': 2 * ratings['great'] + 5 * ratings['good'],
    'good': 7 * ratings['good'],
    'bad': 5 * ratings['good'],
    'terrible': None
}


def get_day_key(day):
    return day.strftime('%Y-%m-%d')


def get_rating_for_day(day):
    return data.get(get_day_key(day), None)


def set_rating_for_day(day, rating):
    assert rating in ratings
    data[get_day_key(day)] = rating


def delete_rating_for_day(day):
    del data[get_day_key(day)]


def rate_week(days, today):
    normal_points = sum(map(lambda day: ratings.get(get_rating_for_day(day), 0), days))
    grace_points = sum(day.year != today.year for day in days)

    return next(rating for rating, level in thresholds.iteritems() if normal_points + grace_points > level)


def get_classes_for_date(day, today):
    statuses = []

    if day.year != today.year:
        statuses.append('not-this-year')
    elif day == today:
        statuses.append('today')
    elif day > today:
        statuses.append('future')

    status = get_rating_for_day(day)
    if status:
        statuses.append(status)
    else:
        statuses.append('nodata')

    return ' '.join(statuses)


def get_week_status(week, today):
    if all(day > today for day in week):
        week_status = 'blank'
    elif any(day > today for day in week):
        week_status = 'pending'
    else:
        week_status = rate_week(week, today)

    return week_status


def week_days_for_year(year, start_day):
    cal = calendar.Calendar(start_day)
    return [day
            for month in range(1, 13)
            for day in cal.itermonthdates(year, month)]


def get_weeks(today=datetime.date.today(), start_day=6):
    weeks = chunk_list(week_days_for_year(today.year, start_day), 7)

    weeks_data = []
    for week in weeks:
        week_data = {
            'days': [{'classes': get_classes_for_date(day, today)} for day in week],
            'status': get_week_status(week, today)
        }

        weeks_data.append(week_data)

    return weeks_data


def application(env, start_response):
    with open('grid_tracker.mustache') as template:
        content = pystache.render(
            template.read(),
            {'weeks': get_weeks()}
        )

    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)

    return [content]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    # simplewsgi is failing on non-str content
    # so we'll use a simple wrapper to force it to str
    # but not affect other wsgi servers

    def force_str_content(application):
        def wrapped(env, start_response):
            return map(str, application(env, start_response))

        return wrapped

    httpd = make_server('', 8888, force_str_content(application))
    httpd.serve_forever()
