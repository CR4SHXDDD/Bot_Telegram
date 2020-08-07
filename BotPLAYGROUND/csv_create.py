import requests
from bs4 import BeautifulSoup as BS
import csv


def get_html(url): #обработка url
    r = requests.get(url)
    if r.ok:
        return r.text
    print(r.status_code)


def write_csv(data): #запись данных
    with open('games.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow((data['name'], data['genres'], data['release'], data['info'], data ['url'], data['photo']))
        

def get_page_data(html): # парсинг игр
    soup = BS (html,'lxml')


    items = soup.find_all('div',class_ = 'item')
    for item in items:
        url = 'https://www.playground.ru' + item.find('div' ,class_ = 'media-heading title').find('a').get('href')
        soup = BS(get_html(url),'lxml')

        gameCard = soup.find('div', class_ = 'gp-game-card-top')

        
        try:
            name = gameCard.find('h1', class_ = 'gp-game-title').text.strip()
            sp = name.split("  ")
            name = sp[0].strip()
        except:
            name = ''

        try:
            genres = gameCard.find('div',class_ = 'genres').text.strip()
            genres = 'Жанры: ' + ", ".join(genres.split('\n\n'))

        except:
            genres = ''

        try:
            releaseList = gameCard.find('div', class_ = 'releases').find_all('div', class_ = 'release-item')
        except:
            releaseList = ''
        release = 'Дата выхода:' + '\n'
        for i in releaseList:
            release += ' '.join(i.text.split()) + '\n'
        release = release.strip()
            
        try:
            info = soup.find('div', class_='description-wrapper').text.strip()
        except:
            info = ''


        try:
            info += '\nРазработчик: ' + gameCard.find('div', class_ = 'game-card-info js-redirect').find('span', itemprop = "name").text.strip()
        except:
            pass


        try:
            info += '\nИздатель: ' + gameCard.find('div', class_ = 'game-card-info js-redirect').find('span', itemprop = "publisher").text.strip()
        except:
            pass


        try:
            photo =  soup.find('div', class_ = 'gp-game-cover').find('a').get('href')
        except:
            photo = ''

        data = { 'name': name,
                 'genres': genres,
                 'release': release,
                 'info': info,
                 'photo': photo,
                 'url': url}


        write_csv(data)


def create_csv(): #перебор страниц

    url = 'https://www.playground.ru/games?release=coming&sort=abc&p='
    while True:
        get_page_data(get_html(url))

        soup = BS(get_html(url), 'lxml')

        try:
            url = 'https://www.playground.ru' + soup.find('ul', class_ = 'pagination').find('a', rel = 'next').get('href')
        except:
            break
                                                                                                                   







def clear_csv(): # очищение csv
    with open('games.csv', 'wb'):
        pass
    create_csv()

