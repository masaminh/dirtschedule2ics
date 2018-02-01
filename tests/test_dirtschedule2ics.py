from collections import namedtuple
from datetime import datetime
from unittest import TestCase
from bs4 import BeautifulSoup
from icalendar import vDate
import dirtschedule2ics.dirtschedule2ics as d2i


class TestDirtSchedule2Ics(TestCase):
    def test_get_racelist(self):
        html = '''<html><body><ul>
<li class="race g2">
<p class="date">1/21（日）</p>
<p class="name">東海ステークス</p>
<p class="course">JRA中京 1800m</p>
<a href="#"></a>
</li>
<li class="race jpn3 mare">
<p class="date">1/24（水）</p>
<p class="name">TCK女王盃</p>
<p class="course">大井 1800m</p>
<a href="dirtrace_01.html"></a>
</li>
<li class="race jpn1">
<p class="date">1/31（水）</p>
<p class="name">川崎記念</p>
<p class="course">川崎 2100m</p>
<a href="dirtrace_05.html"></a>
</li>
</ul></body></html>'''
        races = d2i.get_racelist(html)
        self.assertEqual(len(races), 2)
        self.assertEqual(races[0].grade, 'JpnⅢ')
        self.assertEqual(races[0].date, datetime(2018, 1, 24))
        self.assertEqual(races[0].name, 'TCK女王盃')
        self.assertEqual(races[0].course, '大井競馬場')

    def test_get_race(self):
        html = '''<html><body><ul>
<li class="race jpn3 mare">
<p class="date">1/24（水）</p>
<p class="name">TCK女王盃</p>
<p class="course">大井 1800m</p>
<a href="dirtrace_01.html"></a>
</li>
</ul></body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        race = d2i.get_race(soup.find('li', class_='race'))
        self.assertEqual(race.grade, 'JpnⅢ')
        self.assertEqual(race.date, datetime(2018, 1, 24))
        self.assertEqual(race.name, 'TCK女王盃')
        self.assertEqual(race.course, '大井競馬場')

    def test_get_race_furikae(self):
        html = '''<html><body><ul>
<li class="race jpn3">
<p class="date">4/30（振月）</p>
<p class="name">かきつばた記念</p>
<p class="course">名古屋 1400m</p>
<a href="#"></a>
</li>
</ul></body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        race = d2i.get_race(soup.find('li', class_='race'))
        self.assertEqual(race.grade, 'JpnⅢ')
        self.assertEqual(race.date, datetime(2018, 4, 30))
        self.assertEqual(race.name, 'かきつばた記念')
        self.assertEqual(race.course, '名古屋競馬場')

    def test_get_race_jpn1Central(self):
        html = '''<html><body><ul>
<li class="race jpn1Central">
<p class="date">11/4（日）</p>
<p class="name">JBCスプリント</p>
<p class="course">JRA京都 1200m</p>
<a href="#"></a>
</li>
</ul></body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        race = d2i.get_race(soup.find('li', class_='race'))
        self.assertEqual(race.grade, 'JpnⅠ')
        self.assertEqual(race.date, datetime(2018, 11, 4))
        self.assertEqual(race.name, 'JBCスプリント')
        self.assertEqual(race.course, 'JRA京都競馬場')

    def test_get_race_g1Local(self):
        html = '''<html><body><ul>
<li class="race g1Local">
<p class="date">12/29（土）</p>
<p class="name">東京大賞典</p>
<p class="course">大井 2000m</p>
<a href="#"></a>
</li>
</ul></body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        race = d2i.get_race(soup.find('li', class_='race'))
        self.assertEqual(race.grade, 'GⅠ')
        self.assertEqual(race.date, datetime(2018, 12, 29))
        self.assertEqual(race.name, '東京大賞典')
        self.assertEqual(race.course, '大井競馬場')

    def test_race2event(self):
        Race = namedtuple('Race', ['grade', 'date', 'name', 'course'])
        race = Race('JpnⅢ', datetime(2018, 1, 24), 'TCK女王盃', '大井競馬場')
        event = d2i.race2event(race)
        self.assertEqual(event['SUMMARY'], 'TCK女王盃(JpnⅢ)')
        self.assertEqual(event['DTSTART'].to_ical(), b'20180124')
        self.assertEqual(event['DTEND'].to_ical(), b'20180124')
        self.assertEqual(event['LOCATION'], '大井競馬場')
