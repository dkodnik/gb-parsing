# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import scrapy
import hashlib
from scrapy.utils.python import to_bytes

file_dir = ''


def convert_list(def_list):
    def_list_new = {}
    for i in range(len(def_list) // 2):
        i *= 2
        def_list_new[def_list[i]] = def_list[i + 1]
    return def_list_new


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]

        item['name'] = item['name'][0]
        #item['price'] = item['price'][0]
        item['def_list'] = convert_list(item['def_list'])

        collection.insert_one(item)
        return item


class LmPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        global file_dir
        file_dir = item["name"][0]
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{file_dir}/{image_guid}.jpg'

    def thumb_path(self, request, thumb_id, response=None, info=None):
        thumb_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'_thumbs/{thumb_id}/{file_dir}/{thumb_guid}.jpg'
