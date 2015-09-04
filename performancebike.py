# tmp shitty scraper for performancebike.com until I figure out how to kimono

from bs4 import BeautifulSoup
import math
import os
import re
import urllib
import urllib2

from models import Component


def get_absolute_url(parent_url, relative_url):
  '''Given parent url and relative url, generate the absolute url'''
  base_url = '/'.join(parent_url.split('/')[:-1])
  return '/'.join([base_url, relative_url])


class PageParser(object):
  '''Generic page parser'''

  source = 'performancebike'

  def __init__(self, url):
    self.url = url
    self.page = BeautifulSoup(urllib2.urlopen(url))

  def get_by_selector(self, selector):
    '''Return all tag contents matching selector'''
    return [(tag.string or '').strip().strip(':')
            for tag in self.page.select(selector) if tag]

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

  def parse_currency(self, s):
    '''Parse currency string to a float'''
    return float(s.strip('$').replace(',', ''))


class ProductPageParser(PageParser):
  '''Parser for product page'''
  def parse(self):
    return {
      'name': self.get_first_by_selector('.product_title').strip(),
      'specs': dict(self.parse_table(
        ['#specsDiv > dl > dt', '#specsDiv > dl > dd'])),
      'price': self.parse_currency(
        self.get_first_by_selector('.sr_product_price .sale_price_val') or
        self.get_first_by_selector('.sr_product_price .list_price_val')),
      'source': self.source,
      'url': self.url,
    }


class CatalogPageParser(PageParser):
  '''Parse a single catalog listing page'''
  def parse(self):
    return {
      'product_urls': [tag.get('href') for tag in self.page.select('.product-info h2 a')],
    }


class CategoryParser(PageParser):
  '''Parse a category, given the first page of that category'''
  PAGE_SIZE = 12

  def parse(self):
    return self.get_product_urls()

  def get_product_urls(self):
    '''Given category first page URL (no params), return all product URLs'''
    page_urls = self.get_paginated_urls()
    product_urls = []
    for page_url in page_urls:
      page = CatalogPageParser(page_url)
      product_urls += [
        get_absolute_url(page_url, product_url) for product_url in
        page.parse().get('product_urls', [])
      ]
    return product_urls

  def get_paginated_urls(self):
    '''Given first category URL (no params), return all paginated URLs'''
    num_products = self.get_product_count()
    num_pages = int(math.ceil(num_products / self.PAGE_SIZE))

    urls = [self.url]
    if num_pages > 1:
      urls += [(
        self.url + '?' +
        urllib.urlencode({
          'pageSize': self.PAGE_SIZE,
          'beginIndex': p * self.PAGE_SIZE
        })
      ) for p in xrange(1, num_pages + 1)]
    return urls

  def get_product_count(self):
    '''Given category page, get total product count'''
    # TODO: make this not terrible / hardcoded to DOM assumptions
    page = PageParser(self.url)
    s = page.get_first_by_selector('.item-numbers').strip()
    # It's going to be the last number in this tag
    match = re.search(re.compile('[0-9]+$'), s)
    if match:
      return int(match.group(0))
    return None


if __name__ == '__main__':
  # Test getting all product URLs given the first page of a category
  urls = CategoryParser('http://www.performancebike.com/bikes/SubCategory_10052_10551_400219_-1_400002_400038').parse()
  print "Found %d products" % len(urls)

  # Scrape pages and dump data into sqlite db
  for i, url in enumerate(urls):
    # Don't recreate if URL is already in DB
    # TODO: deduplicate more intelligently
    if not Component.select().where(Component.url == url).exists():
      comp = Component.create(**ProductPageParser(url).parse())
      print "Parsed product %d of %d" % (i+1, len(urls))
    else:
      print "Product %d of %d is already in database; skipping" % (i+1, len(urls))

  for comp in Component.select():
    print '%s (%s) - %s' % (comp.name, comp.price, comp.url)
