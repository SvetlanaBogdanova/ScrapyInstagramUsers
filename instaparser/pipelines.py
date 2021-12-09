# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram
        self.mongo_base['users'].create_index([('target_user_id', 1), ('user_id', 1), ('relationship_type', 1)], unique=True)

    def process_item(self, item, spider):
        collection = self.mongo_base['users']
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            print(f'Дубликат! {item["username"]}')
            # self.mongo_base['users_dub'].insert_one(item)

        return item
