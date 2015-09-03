# tmp shitty scraper for performancebike.com until I figure out how to kimono

from bs4 import BeautifulSoup
import os
import urllib2


def clean(s):
  return s.strip().strip(':')

def parse_currency(s):
  return float(s.strip('$').replace(',', ''))


class PageParser(object):

  def __init__(self, url):
    self.page = BeautifulSoup(urllib2.urlopen(url))

  def parse_page(self):
    # TODO: dump this to a sqlite db or whatever
    return {
      'name': self.get_first_by_selector('.product_title').strip(),
      'specs': dict(self.parse_table(
        ['#specsDiv > dl > dt', '#specsDiv > dl > dd'])),
      'price': parse_currency(
        self.get_first_by_selector('.sr_product_price .sale_price_val') or
        self.get_by_selector('.sr_product_price .list_price_val')),
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

  for url in urls:
    print PageParser(url).parse_page()
