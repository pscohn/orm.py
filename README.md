orm.py
========

A small ORM for Python.

Features
--------

- Basic queries (select, insert, update, order by, limit, offset)
- Simple model interace with foreign keys


Not Features
------------

- Database or table creation, modification, or migration
- Joins, full text search, most other database features


Requirements
------------

- python3
- postgresql
- psycopg2


To do
-----

- python2 support
- better comparison support
- only update fields that have changed
- order by with `get`
- query unique entries
- tests
- improve query interface
- expand sql functionality


Example
===

Tables are not created for you, so you must create them yourself.
Table names should match the class name when converted to underscore-
separated words, so a class UserRelationship will map to the table
"user\_relationship".

Tables must have a serial primary key called "id", and foreign key
fields must be appended with "\_id".

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

Now you can make queries in a script or interpreter:

    u = User.get(id=1)
    m = list(Message.all(user_from=u))

API
---

    user.save()

Saves or updates a Model object.

    user.delete()

Deletes the Model object. Any cascades must be done in table definitions.    


    Model.get(id=None, **kwargs)

Pass in the ID or kwargs matching your model fields.

    Model.all(separator='AND', order_by=None, limit='ALL', offset=None, **kwargs):

`all` yields the results, so you must catch them in a loop or list.

- separator: pass in 'OR' and a kwarg with a list of possible arguments. For example:


    Message.all(separator='OR', user_from=[user_1, user_2])

This will match all messages from either user\_1 or user\_2.

- order\_by: pass in a string with a field name. Prepend '-' to reverse the order.

- limit: Limit results to first n results.

- offset: Integer to offset your search result

- kwargs: each kwarg value can be a single object or a list.


    Model.count(**kwargs)

Returns an integer.

    Model.is_unique(**kwargs)

Returns True or False.

