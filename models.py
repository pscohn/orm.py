#!/usr/bin/env python3

import orm

class User(orm.Model):
    username = orm.Field()
    password = orm.Field()

class Message(orm.Model):
    user_from = orm.ForeignKey(User) # field should be named "user_from_id"
    user_to = orm.ForeignKey(User) # field should be named "user_to_id"
    date_sent = orm.Field()
    body = orm.Field()
    read = orm.Field(default=False)        


