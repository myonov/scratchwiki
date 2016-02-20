import os
import sys

from peewee import *

db = SqliteDatabase('scratch.db')

class Post(Model):
    markdown = TextField()
    html = TextField()

    class Meta:
        database = db

class Tag(Model):
    name = CharField(max_length=64)

    class Meta:
        database = db

if __name__ == '__main__':
    if sys.argv[1] == 'create':
        if os.path.exists('scratch.db'):
            os.remove('scratch.db')
        db.connect()
        db.create_tables([Post, Tag])
