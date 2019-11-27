from datetime import date, timedelta
import json

with open('../../../calendar.json') as json_file:
    urls = []
    data = json.load(json_file)
    for p in data['seasons']:
        # print(p)
        start_month = p['regular_start_month']
        start_day = p['regular_start_day']
        start_year = p['year']
        end_month = p['regular_end_month']
        end_day = p['regular_end_day']
        end_year = p['year'] + 1
        start_date = date(start_year, start_month, start_day)
        end_date = date(end_year, end_month, end_day)
        delta = timedelta(days=1)
        while start_date <= end_date:
            # print(start_date)
            year = str(start_date).split('-')[0]
            month = str(start_date).split('-')[1]
            day = str(start_date).split('-')[2]
            urls.append('https://www.basketball-reference.com/boxscores/?' + 'month=' + month + '&day=' + day +
                        '&year=' + year)
            start_date += delta