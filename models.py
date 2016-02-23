from __future__ import print_function, unicode_literals

import os
import sys
import datetime
import inspect

from peewee import *

db = SqliteDatabase('scratch.db')

def track_tables():
    tables = []
    for cls, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, BasicModel) and obj != BasicModel:
            tables.append(obj)
    return tables

class BasicModel(Model):
    class Meta:
        database = db

class Post(BasicModel):
    markdown = TextField()
    html = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    @property
    def tags(self):
        tag_ids = [t.tag_id for t in TagPost.select().where(TagPost.post_id == self.id)]
        tags = Tag.select().where(Tag.id << tag_ids)
        return tags

    @property
    def tag_names(self):
        return [t.name for t in self.tags]

    def update_tags(self, tags):
        q = TagPost.delete().where(
            TagPost.tag_id << [t.id for t in self.tags]
        ).where(TagPost.post_id == self.id)
        q.execute()

        for tag in tags:
            t, created = Tag.get_or_create(name=tag)
            TagPost.get_or_create(post_id=self.id, tag_id=t.id)

class Tag(BasicModel):
    name = CharField(max_length=64, index=True, unique=True)

class TagPost(BasicModel):
    tag_id = IntegerField(index=True)
    post_id = IntegerField(index=True)

    class Meta:
        indexes = (
            (('tag_id', 'post_id'), True),
        )

if __name__ == '__main__':
    db.connect()
    if len(sys.argv) > 1 and sys.argv[1] == 'create':
        if os.path.exists('scratch.db'):
            os.remove('scratch.db')
        db.create_tables(track_tables())
