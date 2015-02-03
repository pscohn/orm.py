import re
import psycopg2

DELETE = 'DELETE FROM "{table}" WHERE id=%s'
INSERT = 'INSERT INTO "{table}" ({fields}) VALUES ({values}) RETURNING id'
UPDATE = 'UPDATE "{table}" SET {fields} WHERE id=%s'
GET = 'SELECT {fields} from "{table}" WHERE {field}=%s'
ALL = 'SELECT {fields} from "{table}"'
COUNT = 'SELECT id from "{table}"'
ORDER = 'ORDER BY {field} {direction}'
LIMIT = 'LIMIT %s'
OFFSET = 'OFFSET %s'

## UTILS ##

def comma_separated(fields):
    return ', '.join(fields)

def camel_to_underscores(name):
    split = re.split('([A-Z])', name)
    result = ''
    for s in split:
        if s != '':
            if len(s) == 1 and s.isupper():
                result += '_' + s.lower()
            elif len(s) > 1 and s.islower():
                result += s
    result = result.strip('_')
    return result

## ---- connection class ----##

class Connection:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect()
        
    def connect(self):
        self.conn = psycopg2.connect(dbname='rsstest')
        self.cur = self.conn.cursor()

    def execute(self, query, data):
        print('sql: %s' % query)
        self.cur.execute(query, data)
        self.conn.commit()

    def close(self):
        self.conn.close() 

    def __del__(self):
        self.close()

## --- ##

class Field:
    def __init__(self, default=None):
        self.value = default

class ForeignKey:
    def __init__(self, model):
        self.value = None
        self.model = model


class ModelMeta(type):

    def __new__(cls, name, bases, attrs):
        attrs['_class_name'] = name #TODO need this?
        name = camel_to_underscores(name)
        attrs['_table_name'] = name
        fields = {}
        foreign_keys = {}
        for f, v in attrs.items():
            if not f.startswith('_'):
                if isinstance(v, Field):
                    fields[f] = v
                elif isinstance(v, ForeignKey):
                    foreign_keys[f] = v
        attrs['_fields'] = fields
        attrs['_foreign_keys'] = foreign_keys
        return super(ModelMeta, cls).__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    def __init__(self):
        self.id = None
        for k, v in self._fields.items():
            setattr(self, k, v.value)        
        for k, v in self._foreign_keys.items():
            setattr(self, k, v.value)

    def _populate_lists(self):
        fields = []
        values = []
        foreign_keys = []
        fk_values = []
        for key, val in self.__dict__.items():
            if key in self._fields:
                fields.append(key)
                values.append(str(val))
            elif key in self._foreign_keys:
                foreign_keys.append(key+'_id')
                fk_values.append(str(val.id))
        return fields, values, foreign_keys, fk_values

    def _save(self):
        fields, values, fk, fv = self._populate_lists()
        fields += fk
        values += fv
        fields = comma_separated(fields)
        sql = INSERT.format(table=self._table_name, fields=fields, values=', '.join(['%s' for _ in values]))
        c = Connection()
        c.execute(sql, values)
        self.id = c.cur.fetchone()[0]
        c.close()

    def _update(self):
        fields, values, fk, fv = self._populate_lists()
        fields += fk
        values += fv
        values.append(self.id)
        sql = UPDATE.format(table=self._table_name, fields=', '.join([f+'=%s' for f in fields]))
#        print(type(sql), type(values))
#        print(sql, values)
        c = Connection()
        c.execute(sql, values)
        c.close()

    def save(self):
        if self.id is None:
            self._save()
        else:
            self._update()

    def delete(self):
        sql = DELETE.format(table=self.__class__._table_name)
        data = (self.id,)
        c = Connection()
        c.execute(sql, data)
        c.close()

    @classmethod
    def get(cls, id=None, **kwargs):
        if id is not None:
            fields = cls._get_fields()
            sql = GET.format(fields=comma_separated(fields), table=cls._table_name, field='id')
            data = (id,)
            c = Connection()
            c.execute(sql, data)
            o = cls.objectify(c.cur.fetchone(), fields)
            o.id = id
            c.close()
            return o

        for key, val in kwargs.items():
            fields = ['id'] + cls._get_fields()
            valid_key = False
            if key in cls._fields.keys():
                valid_key = True
                final_key = key
                data = (val,)
            elif key in cls._foreign_keys.keys():
                valid_key = True
                final_key = key+'_id'
                data = (val.id,)

            if valid_key:
                sql = GET.format(fields=comma_separated(fields), table=cls._table_name, field=final_key)
                c = Connection()
                c.execute(sql, data)
                o = cls.objectify(c.cur.fetchone(), fields)
                c.close()
                return o

    @classmethod
    def all(cls, separator='AND', order_by=None, limit='ALL', offset=None, count=False, **kwargs):
        fields = ['id'] + cls._get_fields()

        if len(kwargs) == 0:
            sql = ALL.format(fields=comma_separated(fields), table=cls._table_name)
            data = ()

        else:
            sql = ALL
            i = 0
            values = []
            for key, val in kwargs.items():
                begin = ' WHERE ' if i==0 else ' %s ' % separator
                if type(val) == list:
                    for v in val:
                        if key in cls._foreign_keys:
                            values.append(v.id)
                            sql += begin + '{key}=%s'.format(key=key+'_id')
                        elif key in cls._fields:
                            values.append(v)
                            sql += begin + '{key}=%s'.format(key=key)
                else:
                    if key in cls._foreign_keys:
                        values.append(val.id)
                        sql += begin + '{key}=%s'.format(key=key+'_id')
                    elif key in cls._fields:
                        values.append(val)
                        sql += begin + '{key}=%s'.format(key=key)
                i += 1

            if order_by is not None:
                order = 'DESC' if order_by.startswith('-') else 'ASC'
                ordersql = ORDER.format(field=order_by.strip('-'), direction=order)
                sql += ' ' + ordersql
            if limit != 'ALL' and limit is not None:
                sql += ' ' + LIMIT
                values.append(limit)
            if offset is not None:
                sql += ' ' + OFFSET
                values.append(offset)

            sql = sql.format(fields=comma_separated(fields), table=cls._table_name)
            data = tuple(values)

        c = Connection()
        c.execute(sql, data)
        if count:
            count = 0
            for cur in c.cur.fetchall():
                count += 1
            return count

        for cur in c.cur.fetchall():
            o = cls.objectify(cur, fields)
            yield o
        c.close()
        return


    @classmethod
    def is_unique(cls, **kwargs):
        o = list(cls.all(**kwargs))
        if o is None or len(o) == 0:
            return True
        else:
            return False

    @classmethod
    def count(cls, **kwargs):
        count = 0
        for o in cls.all(count=True, **kwargs):
            count += 1
        return count

    @classmethod
    def _get_fields(cls):
        return list(cls._fields.keys()) + list(map(lambda x: x+'_id', cls._foreign_keys.keys()))
        
 
    @classmethod
    def objectify(cls, cur, fields):
        if cur is None:
            return None
        o = cls()
        for i, f in enumerate(cur):
            cleaned_field = fields[i][:-3] if fields[i].endswith('_id') else fields[i]
            if cleaned_field in cls._foreign_keys:
                model = cls._foreign_keys[cleaned_field].model
                obj = model.get(id=f)
                setattr(o, cleaned_field, obj)
            elif fields[i] in cls._fields:
                setattr(o, fields[i], f)
            elif fields[i] == 'id':
                setattr(o, 'id', f)
        return o
