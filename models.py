#!/usr/bin/env python3

import orm

''' You should first set up tables named "user" and "message" '''
class User(orm.Model):
    username = orm.Field()
    password = orm.Field()

    def get_all_received_messages(self):
        ''' You could also pass in a limit and offset, or yield results
            one at a time.
        '''
        return list(Message.all(user_to=self, order_by='-date_sent'))

    def get_all_sent_messages(self):
        return list(Message.all(user_from=user, order_by='-date_sent'))

class Message(orm.Model):
    user_from = orm.ForeignKey(User) # field should be named "user_from_id"
    user_to = orm.ForeignKey(User) # field should be named "user_to_id"
    date_sent = orm.Field()
    body = orm.Field()
    read = orm.Field(default=False)        


