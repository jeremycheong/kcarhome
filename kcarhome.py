import os

import config as cfg
from parserpage import htmlparser, getclasses, getclassbrandurl

TEST_URL = 'https://product.360che.com/img/c1_s65_b31_s116.html'

def get_brand_name(brand_url):
    sub_brand_soup = htmlparser(TEST_URL)
    brand_name_tag_list = sub_brand_soup.find('div', 'map_mal').find_all('a')[-3:]
    brand_name = '_'.join(list(map(lambda brand_name_tag: brand_name_tag.get_text().replace('图片库', ''), brand_name_tag_list)))
    print(brand_name)



if __name__ == "__main__":
    get_brand_name(cfg.domain)

    