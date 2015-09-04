# tmp shitty scraper for performancebike.com until I figure out how to kimono

from bs4 import BeautifulSoup
import math
import os
import re
import urllib
import urllib2

from models import Component


def clean(s):
  return s.strip().strip(':')

def parse_currency(s):
  return float(s.strip('$').replace(',', ''))


PAGE_SIZE = 12
#http://www.performancebike.com/bikes/SubCategory_10052_10551_400219_-1_400002_400038?beginIndex=12&pageSize=12

def get_product_count(category_url):
  '''Given category page, get total product count'''
  # TODO: make this not terrible / hardcoded to DOM assumptions
  page = PageParser(category_url)
  s = page.get_first_by_selector('.item-numbers').strip()
  match = re.search(re.compile('[0-9]+$'), s)
  if match:
    return int(match.group(0))
  return None

def get_paginated_urls(category_url):
  '''Given first page's URL (no params), return all available paginated URLs'''
  num_products = get_product_count(category_url)
  num_pages = int(math.ceil(num_products / PAGE_SIZE))

  urls = [category_url]
  if num_pages > 1:
    for p in xrange(1, num_pages + 1):
      urls.append(
        category_url + '?' +
        urllib.urlencode({'pageSize': PAGE_SIZE, 'beginIndex': p * PAGE_SIZE})
      )
  return urls

def get_product_urls(category_url):
  '''Given category first page URL (no params), return all product URLs'''
  pass


class PageParser(object):

  source = 'performancebike'

  def __init__(self, url):
    self.page = BeautifulSoup(urllib2.urlopen(url))

  def parse_page(self):
    return {
      'name': self.get_first_by_selector('.product_title').strip(),
      'specs': dict(self.parse_table(
        ['#specsDiv > dl > dt', '#specsDiv > dl > dd'])),
      'price': parse_currency(
        self.get_first_by_selector('.sr_product_price .sale_price_val') or
        self.get_by_selector('.sr_product_price .list_price_val')),
      'source': self.source,
    }
  
  def get_by_selector(self, selector):
    '''Return all tag contents matching selector'''
    return [clean(tag.string) for tag in self.page.select(selector) if tag]

  def get_first_by_selector(self, selector):
    '''Return content of first tag matching selector'''
    tags = self.page.select(selector)
    if not tags:
      return None
    return tags[0].string

  def parse_table(self, selectors):
    '''
    Given list of selectors, return list of tuples containing table row data
    '''
    return zip(*(self.get_by_selector(selector) for selector in selectors))


if __name__ == '__main__':
  urls = [
    # component page
    'http://www.performancebike.com/bikes/Product_10052_10551_1175974_-1_400222__400222',
    # full bike page
    'http://www.performancebike.com/bikes/Product_10052_10551_1161804_-1_400317__400317',
  ]

  # Scrape pages and dump data into sqlite db
  #for url in urls:
  #  comp = Component.create(**PageParser(url).parse_page())

  for comp in Component.select():
    print '%s (%s) - %s' % (comp.name, comp.price, comp.source)

  print get_paginated_urls('http://www.performancebike.com/bikes/SubCategory_10052_10551_400219_-1_400002_400038')

