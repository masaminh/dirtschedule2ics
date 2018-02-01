import argparse
from collections import namedtuple
from datetime import datetime
import re
import sys
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vDate
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='?',
                        default='http://www.keiba.go.jp/dirtrace/schedule.html'
                        )
    parser.add_argument('-o', '--output', nargs='?',
                        type=argparse.FileType(mode='w'), default=sys.stdout)
    args = parser.parse_args()
    response = requests.get(args.input)
    response.encoding = response.apparent_encoding

    ical = Calendar()
    for race in get_racelist(response.text):
        ical.add_component(race2event(race))

    args.output.write(ical.to_ical().decode('utf-8'))


def get_racelist(html):
    soup = BeautifulSoup(html, 'html.parser')
    race = soup.findAll('li', class_='race')

    return [x for x in (get_race(x) for x in race)
            if not x.course.startswith('JRA')]


def get_race(race):
    grade_code = race.get('class')[1]
    grade_table = {'jpn1': 'JpnⅠ', 'jpn2': 'JpnⅡ', 'jpn3': 'JpnⅢ',
                   'g1': 'GⅠ', 'g2': 'GⅡ', 'g3': 'GⅢ', 'jpn1Central': 'JpnⅠ',
                   'g1Local': 'GⅠ'}
    grade = grade_table[grade_code]
    date_string = race.find('p', class_='date').string
    date_match = re.fullmatch(r'(\d{1,2})/(\d{1,2})（.+）', date_string)
    date = datetime(2018, int(date_match.group(1)), int(date_match.group(2)))
    name = race.find('p', class_='name').string
    course = race.find('p', class_='course').string.split()[0] + '競馬場'

    Race = namedtuple('Race', ['grade', 'date', 'name', 'course'])

    return Race(grade, date, name, course)


def race2event(race):
    event = Event()
    event.add('SUMMARY', race.name + '(' + race.grade + ')')
    event.add('DTSTART', vDate(race.date))
    event.add('DTEND', vDate(race.date))
    event.add('LOCATION', race.course)
    event.add('TRANSP', 'TRANSPARENT')
    return event


if __name__ == '__main__':
    main()
