import json
from peewee import *


db = SqliteDatabase('bikebot.db')

def before_request_handler():
    db.connect()

def after_request_handler():
    db.close()


# TODO: we should probably just use Django haha
class JsonField(TextField):
  def db_value(self, value):
    return json.dumps(value)

  def python_value(self, value):
    if isinstance(value, basestring):
      return json.loads(value)
    return value


class Component(Model):
  class Meta:
    database = db

  name = CharField()
  price = FloatField()  # USD
  specs = JsonField()  # dictionary of specs
  source = CharField()  # source of info
  url = CharField()


# TODO: this should be somewhere safer
db.connect()
Component.create_table(True)


if __name__ == '__main__':
  for comp in Component.select():
    print comp.name, comp.price
