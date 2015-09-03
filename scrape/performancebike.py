# tmp shitty scraper for performancebike.com until I figure out how to kimono

from bs4 import BeautifulSoup
import urllib


def clean(s):
  return s.strip().strip(':')

def parse_currency(s):
  return float(s.strip('$').replace(',', ''))


def fetch_page(url):
  fname = 'tempfile'
  urllib.urlretrieve(url, fname)
  doc = BeautifulSoup(open(fname, 'r'))

  def get_by_selector(selector):
    return [clean(tag.string) for tag in doc.select(selector) if tag]

  def get_first_by_selector(selector):
    tags = doc.select(selector)
    if not tags:
      return None
    return tags[0].string

  def parse_table(selectors):
    '''
    Given list of selectors, return list of tuples containing table row data
    '''
    return zip(*(get_by_selector(selector) for selector in selectors))

  return {
    'name': get_first_by_selector('.product_title').strip(),
    'specs': dict(parse_table(['#specsDiv > dl > dt', '#specsDiv > dl > dd'])),
    'price': parse_currency(
      get_first_by_selector('.sr_product_price .sale_price_val') or
      get_by_selector('.sr_product_price .list_price_val')),
  }

if __name__ == '__main__':
  # component page
  print fetch_page('http://www.performancebike.com/bikes/Product_10052_10551_1175974_-1_400222__400222')
  # full bike page
  print fetch_page('http://www.performancebike.com/bikes/Product_10052_10551_1161804_-1_400317__400317')
