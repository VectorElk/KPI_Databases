from lxml import etree


def parse_text(str):
    for symbol in str:
        if symbol != " ":
            continue
        else:
            return True
    return False

def filter_links(links):
    filtered_links = []
    for link in links:
        if link.startswith("http://ru.golos.ua"):
            filtered_links.append(link)
    return filtered_links


def parse_webpage():
    root = etree.Element('data')
    xml_file = etree.ElementTree(root)
    parser = etree.HTMLParser(encoding='UTF-8')
    tree = etree.parse('http://ru.golos.ua/', parser)
    links  = tree.xpath('//a/@href')
    links = filter_links(links)
    counter = 0
    i = 0
    while counter <= 20:
        try:
            currTree = etree.parse(links[i], parser)
            images = currTree.xpath('//img/@src')
            texts = currTree.xpath('//*[text()]')
            if texts and images:
                page_el = etree.SubElement(root, 'page', url=links[counter])
                for t in texts:
                    if (t.tag != "script" and "style") and t.text and parse_text(t.text):
                        text_el = etree.SubElement(page_el, 'fragment', type='text')
                        text_el.text = t.text
                for img in images:
                    image_el = etree.SubElement(page_el, 'fragment', type='image')
                    image_el.text = img
            counter += 1
        except IOError as error:
            pass
        i += 1
    xml_file.write('golos.xml', xml_declaration=True, encoding='utf-8')