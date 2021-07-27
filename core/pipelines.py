# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CorePipeline:
    def process_item(self, item, spider):
        return item


class MetalArchivesMongoDB:

    def __init__(self, mongo_uri, mongo_db):
        self._collection_name = 'metal_bands'
        self._mongo_uri = mongo_uri
        self._mongo_db = mongo_db
        self._client = None
        self._db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        self._client = pymongo.MongoClient(self._mongo_uri)
        self._db = self._client[self._mongo_db]

    def close_spider(self, spider):
        self._client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        num_docs = self._db[self._collection_name].count_documents({
            'band_id': adapter.get('band_id')
        })
        if num_docs > 0:
            raise DropItem('Item {} already inserted'.format(adapter.get('band_id')))
        else:
            self._db[self._collection_name].insert_one(ItemAdapter(item).asdict())
        return item
