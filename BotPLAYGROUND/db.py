from db_create import Game, List
from Levenshtein import _levenshtein
from Levenshtein._levenshtein import *
selGame = Game.select()
selList = List.select()



import requests
from bs4 import BeautifulSoup as BS


def search_game_equals(name):
    for  gn in selGame:
        if (name == gn.name):
            return (gn.name)
    return ''

def search_game(name): # сравнение введенного названия пользователем и названия в базе данных
    for gn in selGame:
        if (jaro(gn.name, name) > 0.80):
            return (gn.name)
def show_info (name):
    return



def information_conclusion(name): # вывод данные из базы Game
    infor = Game.get(Game.name == name)
    return (infor.name + '\n' + infor.genres + '\n'  + infor.release + '\n' + infor.info)

def get_photo(name):
    infor = Game.get(Game.name == name)
    return (infor.photo)

def print_game(id): #вывод из базы List игр пользователя
    id_us = List.get_or_none(List.id_user == id)
    if (id_us == None):
        return ("У вас нет ни одной игры в списке")

    gam = selList.where(List.id_user == id)
    f = str()
    for game in gam:
        for i in game.games:
            f += i + '\n'
        return (f.strip())




def add_game(id, name, url): # Добавление подписки если пользователь не был подписан на эту игру
    id_us = List.get_or_none(List.id_user == id)
    if (id_us != None):
        listPost = List.get (List.id_user == id)

        for i in listPost.games:
            if (i == name):
                return False
            else:
                listPost.games[name] = url
                listPost.save()
                return True
    else:

        List(id_user = id, games = {name : url}).save()
        return True




def renovation_post(): # проверка выхода новых статей

    for game in selList:

        for line, key in game.games.items():

            name = Game.get(Game.name == line)
            url = name.url
            urlPost = get_page_url(get_html(url))
            if (key != urlPost):

                game.games[line] = urlPost
                data = parser_post(urlPost)
                return game.id_user, data
            else:

                return False, False







def get_page_url(html):
    soup = BS(html, 'lxml')
    post = soup.find('div', class_='post-title').find('a').get('href')
    return (post)


def get_html(url):
    r = requests.get(url)
    if r.ok:
        return r.text
    print(r.status_code)


def get_page_data(html): # парсер статей
    soup = BS(html, 'lxml')
    post = soup.find('div', class_='post-title').find('a').get('href')
    soup = BS(get_html(post), 'lxml')
    h1 = soup.find('h1').text.strip()

    try:
        info = soup.find('div', class_="article-content user-blog-content js-post-item-content").text.strip()
    except:
        info = ''
    counter = 0

    try:
        photoFind = soup.find('div', class_="article-content user-blog-content js-post-item-content").find_all('figure')
        listPhoto = []
        for i in photoFind:
            if (counter < 5):
                listPhoto.append(i.find('a').get('href'))
                counter += 1
    except:
        pass

    try:
        videoFind = soup.find('div', class_="article-content user-blog-content js-post-item-content").find(
            'pg-embed').get('src')
        video = 'Видео можно посмотреть по этой ссылке: ' + 'https://www.playground.ru/video/iframe/' + videoFind

    except:
        video = ''

    data = {
        "title": h1,
        "info": info,
        "image": listPhoto,
        "video": video,
        "url": post,
        "counter": counter
    }

    return (data)


def parser_post(url):
    return get_page_data(get_html(url))

    

