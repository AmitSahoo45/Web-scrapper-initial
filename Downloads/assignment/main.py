import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
from datetime import datetime, date
import os

if not os.path.exists('csv_files'):
    os.mkdir('csv_files')

today = date.today().strftime('%d%m%Y')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

url = 'https://www.theverge.com'
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')

articles = soup.find_all('article', class_='c-entry-box--compact__body')

csv_file = open(f'csv_files/{today}_verge.csv',
                'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id', 'URL', 'headline', 'author', 'date'])

conn = sqlite3.connect('theverge.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS articles
             (id INTEGER PRIMARY KEY, url TEXT, headline TEXT, author TEXT, date TEXT)''')

for i, article in enumerate(articles):
    headline = article.find(
        'h2', class_='c-entry-box--compact__title').text.strip()
    url = article.find('a', href=True)['href']

    byline = article.find('span', class_='c-byline__item')
    if byline:
        author = byline.text.strip()
    else:
        author = 'N/A'
    date = article.find('time', class_='c-byline__item')['datetime']
    date = datetime.strptime(
        date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

    csv_writer.writerow([i+1, url, headline, author, date])

    c.execute("INSERT OR IGNORE INTO articles (id, url, headline, author, date) VALUES (?, ?, ?, ?, ?)",
              (i+1, url, headline, author, date))

conn.commit()
conn.close()

csv_file.close()
