import argparse
from lxml import etree

def evaluate_texts():
    data_file = 'golos.xml'
    avg = etree.parse(data_file).xpath("count(//fragment[@type='text']) div count(//page)")
    print('Task 2 count:', avg)