#coding==utf-8

import requests
import os
import re
from bs4 import BeautifulSoup
import config as cfg
from tqdm import tqdm
import time


def htmlparser(url):  #解析网页的函数
    request_ok = False
    soup = None
    while(not request_ok):
        try:
            r = requests.get(url, headers=cfg.headers)  #get请求
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            content = r.text
            soup = BeautifulSoup(content, "html.parser")
            request_ok = True
        except:
            print('Request {} failed! wait and try againe...'.format(url))
            time.sleep(1.5)

    return soup


def getclasses(url):
    soup = htmlparser(url)
    k_classes = soup.find_all("div", "pro_big_b")
    pick_url = []
    for k_class in k_classes:
        # print(k_class.find('a').get('href'))
        # print(k_class.find('a').get_text())
        pick_url.append(k_class.find('a').get('href'))
    pick_url = pick_url[0:5]
    # print(pick_url)
    return pick_url


def transimagename(kcar_img_url):
    jpg_path_start_idx = kcar_img_url.find('imgc')
    jpg_path_end_idx = kcar_img_url.find('_')
    jpg_name = '_'.join(
        kcar_img_url[jpg_path_start_idx:jpg_path_end_idx].split('/'))
    return jpg_name

class ModelInfo:
    def __init__(self):
        self.model_name = ''  # 车型
        self.urls = []  # 图片url地址

def savemodelimg(model_info, save_model_image_dir):
    model_name = model_info.model_name.strip().replace('/', '_')
    urls = model_info.urls
    save_model_image_dir = os.path.join(save_dir_root, model_name)
    print('save_model_image_dir: ', save_model_image_dir)
    if not os.path.exists(save_model_image_dir):
        print('creat dir: ', save_model_image_dir)
        os.mkdir(save_model_image_dir)
    print('image urls num: ', len(urls))
    for img_url in urls:
        request_ok = False
        image_name = transimagename(img_url)
        # 保存该车型图片
        image_save_path = os.path.join(save_model_image_dir,
                                        image_name)
        img_req = None
        while(not request_ok):
            try:
                img_req = requests.get(img_url, stream=True)
                request_ok = True
            except:
                print('save image url: {} failed! wait and try againe...'.format(img_url))
                time.sleep(1.5)
        
        with open(image_save_path, 'wb') as f:
            for chunk in img_req.iter_content(chunk_size=32):
                f.write(chunk)
        print('save image: ' +  image_save_path + " done!")
        time.sleep(0.5)


def getmodelinfo(model_url_parent):
    image_url_list = []
    model_url = model_url_parent.get('href')

    # 得到外观url并获取车型下的所有图片url
    model_outward_url = htmlparser(model_url).find_all(
        'div', 's_pickupin')[0].find_all('a')[1].get('href')
    image_tags = htmlparser(model_outward_url).find_all(
        'div', 'imgname_b_cent')[0].find_all('img')
    for image_tag in image_tags:
        image_url = image_tag.parent.get("href").replace(
            "Pic", "Pic_big")
        image_big_src_url = htmlparser(image_url).find_all(
            id='imgid')[0].get('src')
        print("\t" + image_big_src_url)
        image_url_list.append(image_big_src_url)

    return image_url_list


def get_brand_name(sub_brand_soup):
    brand_name_tag_list = sub_brand_soup.find('div', 'map_mal').find_all('a')[-3:]
    brand_name = '_'.join(list(map(lambda brand_name_tag: brand_name_tag.get_text().replace('图片库', ''), brand_name_tag_list)))
    return brand_name

def getmodelurltags(sub_brand_tags, save_image_root):
    # print('sub_brand_tags: ', sub_brand_tags)
    # return
    # model_info_tags_list = []
    for sub_brand_tag in sub_brand_tags:
        model_info = ModelInfo()
        sub_brand_url = sub_brand_tag.get('href')
        # print("sub_brand_url: ", sub_brand_url)
        # return
        model_soup = htmlparser(sub_brand_url)
        model_info.model_name = get_brand_name(model_soup)
        model_tags = model_soup.find_all('div', 'imgname_b_cent di')[0]
        # print("model_tags: \n", (model_tags))
        # return
        # for model_tag in model_tags:
        model_url_tags = model_tags.find_all(['img'])  #该品牌下，子品牌的所有车型
        # print('model_url_tags len: ', len(model_url_tags))
        for model_url_tag in model_url_tags:
            model_url_parent = model_url_tag.parent  #.get('href')
            model_images_url_list = getmodelinfo(model_url_parent)
            model_info.urls.extend(model_images_url_list)

        savemodelimg(model_info, save_image_root)

        # model_info_tags_list.append(model_info)
        
    # return model_info_tags_list
    

def getclassbrandurl(class_url):
    soup = htmlparser(class_url)
    brand_tags = soup.find_all("div", "newtree")

    sub_brand_tags_list = []
    print("brand_tags: ", len(brand_tags))
    # return
    for brand_tag in tqdm(brand_tags):
        brand_url = brand_tag.find('a').get('href')
        # print('brand_url: ', brand_url)
        brand_soup = htmlparser(brand_url)
        sub_brand_tags = brand_soup.find_all("dl", "newshow")[0]

        sub_brand_tags = sub_brand_tags.find_all('a')  #.get('href')
        # print(sub_brand_tags)

        sub_brand_tags_list.append(sub_brand_tags)

    return sub_brand_tags_list
        # print("sub_brand_tags: \n", (sub_brand_tags))
        # return




def spiderpipeline(base_url, save_dir_root):
    classes_urls = getclasses(base_url)  #卡车类型，如轻卡，牵引车等
    print('get big class: ', len(classes_urls))
    for class_url in classes_urls:
        sub_brand_tags_list = getclassbrandurl(class_url)   #卡车类型中所有的品牌
        print('get sub brand num: ', len(sub_brand_tags_list))
        for sub_brand_tags in sub_brand_tags_list:
            getmodelurltags(sub_brand_tags, save_dir_root)   # 具体车型的url tag 列表
    print('Done!')



if __name__ == '__main__':
    save_dir_root = '/home/zhangym/DataSpace/car/kcarhome_image'
    spiderpipeline(cfg.domain, save_dir_root)


