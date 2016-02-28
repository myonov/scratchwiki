from __future__ import print_function, unicode_literals

import os
import sys
import datetime
import inspect
import math

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

    @classmethod
    def relevant_posts(cls, tags=None):
        positives, negatives = Tag.filter_tags(tags)
        positive_tag_ids = [t.id for t in Tag.select().where(Tag.name << positives)]
        negative_tag_ids = [t.id for t in Tag.select().where(Tag.name << negatives)]

        negatives_join = TagPost.select(TagPost.post_id).join(
            Tag,
            JOIN_INNER,
            on=(TagPost.tag_id == Tag.id)
        ).where(Tag.id << negative_tag_ids)
        negatives_join = negatives_join.alias('nj')

        lp = len(positives)
        if lp > 0:
            positives_join = TagPost.select(TagPost.post_id).join(
                Tag,
                JOIN_INNER,
                on=(TagPost.tag_id == Tag.id)
            ).where(Tag.id << positive_tag_ids).group_by(
                TagPost.post_id
            ).having(fn.Count(Tag.id) == lp)
        else:
            positives_join = TagPost.select(TagPost.post_id).distinct()
        positives_join = positives_join.alias('pj')

        req = Post.select().join(
            negatives_join,
            JOIN_LEFT_OUTER,
            on=(Post.id == negatives_join.c.post_id)
        ).join(
            positives_join,
            JOIN_INNER,
            on=(Post.id == positives_join.c.post_id)
        ).where(negatives_join.c.post_id == None).order_by(
            Post.created_at.desc()
        )

        return req

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
            with db.transaction():
                t, created = Tag.get_or_create(name=tag)
                TagPost.get_or_create(post_id=self.id, tag_id=t.id)

    def remove(self):
        self.update_tags([])
        self.delete_instance()

class Tag(BasicModel):
    name = CharField(max_length=64, index=True, unique=True)

    @classmethod
    def filter_tags(cls, tags):
        if tags is None:
            tags = []

        positives = []
        negatives = []
        for t in tags:
            if t.startswith('-'):
                negatives.append(t[1:])
            else:
                positives.append(t)

        return positives, negatives

class TagPost(BasicModel):
    tag_id = IntegerField(index=True)
    post_id = IntegerField(index=True)

    class Meta:
        indexes = (
            (('tag_id', 'post_id'), True),
        )


class Pager(object):
    POSTS_PER_PAGE = 10

    def __init__(self, q, current_page, posts_per_page=POSTS_PER_PAGE):
        self.q = q
        self.total_count = self.q.count()
        self.posts_per_page = posts_per_page
        if current_page < 1:
            current_page = 1
        if current_page > self.pages:
            current_page = self.pages
        self.current_page = current_page

    @property
    def current(self):
        return self.current_page

    @property
    def pages(self):
        return int(math.ceil((self.total_count) / float(self.posts_per_page)))

    @property
    def has_prev_page(self):
        return self.current_page > 1

    @property
    def has_next_page(self):
        return self.current_page < self.pages

    @property
    def prev(self):
        return self.current_page - 1

    @property
    def next(self):
        return self.current_page + 1

    @property
    def posts(self):
        return self.q.paginate(self.current_page, self.posts_per_page)

if __name__ == '__main__':
    db.connect()
    if len(sys.argv) > 1 and sys.argv[1] == 'create':
        if os.path.exists('scratch.db'):
            os.remove('scratch.db')
        db.create_tables(track_tables())
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        not_used_tags = Tag.select().join(
            TagPost,
            JOIN_LEFT_OUTER,
            on=(Tag.id == TagPost.tag_id)).where(
            TagPost.tag_id == None
        )
        not_used_tags = [t.id for t in not_used_tags]
        q = Tag.delete().where(Tag.id << not_used_tags)
        q.execute()
