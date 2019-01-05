"""ダートグレード競走のスケジュール一覧をiCalendar形式にする."""
import argparse
import re
import sys
from collections import namedtuple
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vDate


def main():
    """メイン関数."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='?',
                        default='http://www.keiba.go.jp/dirtrace/schedule.html'
                        )
    parser.add_argument('-o', '--output', nargs='?',
                        type=argparse.FileType(mode='w'), default=sys.stdout)
    args = parser.parse_args()
    response = requests.get(args.input)

    ical = Calendar()
    for race in get_racelist(response.content):
        ical.add_component(race2event(race))

    args.output.write(ical.to_ical().decode('utf-8'))


def get_racelist(html):
    """レース情報のリストの取得."""
    soup = BeautifulSoup(html, 'html.parser')
    race = soup.findAll('li', class_='race')
    year_line = soup.h3.string
    match = re.fullmatch(r'レース一覧（(\d{4})年）', year_line)
    year = int(match.group(1))

    return [x for x in (get_race(x, year) for x in race)
            if not x.course.startswith('JRA')]


def get_race(race, year):
    """レース情報の取得."""
    grade_code = race.get('class')[1]
    grade_table = {'jpn1': 'JpnⅠ', 'jpn2': 'JpnⅡ', 'jpn3': 'JpnⅢ',
                   'g1': 'GⅠ', 'g2': 'GⅡ', 'g3': 'GⅢ', 'jpn1Central': 'JpnⅠ',
                   'g1Local': 'GⅠ'}
    grade = grade_table[grade_code]
    date_string = race.find('p', class_='date').string
    date_match = re.fullmatch(r'(\d{1,2})/(\d{1,2})（.+）', date_string)
    date = datetime(year, int(date_match.group(1)), int(date_match.group(2)))
    name = race.find('p', class_='name').string
    course = race.find('p', class_='course').string.split()[0] + '競馬場'

    Race = namedtuple('Race', ['grade', 'date', 'name', 'course'])

    return Race(grade, date, name, course)


def race2event(race):
    """レース情報をiCalendarのイベントに変換する."""
    event = Event()
    event.add('SUMMARY', race.name + '(' + race.grade + ')')
    event.add('DTSTART', vDate(race.date))
    event.add('DTEND', vDate(race.date))
    event.add('LOCATION', race.course)
    event.add('TRANSP', 'TRANSPARENT')
    return event


if __name__ == '__main__':
    main()
