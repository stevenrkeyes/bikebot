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


if __name__ == '__main__':
  db.connect()
  Component.create_table(True)

  Component.create(name="fancy-ass wheelset", price=1099.99, specs={u'tire size': u'700C', u'rating': u'4.5', u'weight': u'1570g', u'lacing pattern': u'Front: Radial; Rear: Radial/2-Cross', u'accessories included': u'2 pair of Cryo Blue Brake Pads', u'hub': u'Reynolds Racing', u'skewers included': u'Yes', u'spacing': u'Front: 100mm; Rear: 130mm', u'rim width': u'20.8mm', u'spoke count': u'Front: 20; Rear: 24', u'rim height': u'46mm', u'video': u'WALJK8Wh7I0', u'spokes': u'Bladed', u'compatibility': u'Shimano/SRAM 9/10/11-speed', u'tire type': u'Clincher'})

  component = Component.select().where(Component.name == 'fancy-ass wheelset')[0]
  print component.name, component.price
