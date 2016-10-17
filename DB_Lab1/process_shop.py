from lxml import html
from lxml import etree
import requests


def parse_shop():
    page = requests.get('http://petmarket.ua/zootovary-dlja-ryb/fish-food/')

    root = etree.Element('data')
    doc = etree.ElementTree(root)

    tree = html.fromstring(page.content)
    name = tree.xpath('//div[@class="name"]//text()')
    image = tree.xpath('//div[@class="image"]/a/img/@src')
    price = tree.xpath('//div[@class="price"]/div/text() | //div[@class="price"]/text()')
    price = clean_prices(price)
    for i in range(0, 20):
        product_element = etree.SubElement(root, 'product')

        image_element = etree.SubElement(product_element, 'image')
        image_element.text = image[i]

        name_element = etree.SubElement(product_element, 'name')
        name_element.text = name[i]

        price_element = etree.SubElement(product_element, 'price')
        price_element.text = price[i]

        doc.write('petmarket.xml', xml_declaration=True, encoding='utf-8', pretty_print=True)

def clean_prices(prices):
    return list(filter(lambda s: s and not s.startswith('0'), [price.strip('\n\r\t \xa0') for price in prices]))