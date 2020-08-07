import csv
from peewee import *
from playhouse.postgres_ext import JSONField

db = PostgresqlDatabase(database='gameInfo', user='postgres',password='19537',host = 'localhost')

class Game(Model):
    name = CharField()
    genres = CharField()
    release = CharField()
    info = TextField()
    url = CharField()
    photo = CharField()


    class Meta:
        database = db

class List(Model):
    id_user = CharField()
    games = JSONField()

    class Meta:
        database = db



def create_db(): #подключение к бд; запись информации

    db.connect()
    print('Подключение к бд')
    db.drop_tables([Game], safe = True)
    print('Удаление таблиц')
    db.create_tables([Game], safe = True)
    print('Создание таблиц')
    
    with open('games.csv', encoding='utf-8') as f:
        order = ['name', 'genres', 'release', 'info', 'url', 'photo']
        reader = csv.DictReader(f, fieldnames=order)

        games = list(reader)

        with db.atomic():
           for row in games:
               Game.create(**row)

                                                                                                                   

