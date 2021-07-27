# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MetalArchiveItem(scrapy.Item):
    band_id = scrapy.Field()
    band_name = scrapy.Field()
    country_of_origin = scrapy.Field()
    location = scrapy.Field()
    status = scrapy.Field()
    formed_in = scrapy.Field()
    years_active = scrapy.Field()
    genre = scrapy.Field()
    lyrical_themes = scrapy.Field()
    current_label = scrapy.Field()
    band_logo = scrapy.Field()
    band_img = scrapy.Field()
    band_albums = scrapy.Field()
    band_members = scrapy.Field()
