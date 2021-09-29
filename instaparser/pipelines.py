# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv


class InstaparserPipeline:
    def __init__(self):
        self.file_name = 'insta.csv'
        fields = [
            "user_id",
            "post_id",
            "likes",
            "time"
        ]
        self.item_save(fields)

    def process_item(self, item, spider):
        fields = [
            item['user_id'],
            item['post']['id'],
            item['likes'],
            item['timestamp']
        ]
        self.item_save(fields)

        return item

    def item_save(self, data):
        with open(self.file_name, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)
