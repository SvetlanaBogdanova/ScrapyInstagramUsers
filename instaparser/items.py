# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UserParserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    target_user_id = scrapy.Field()
    target_username = scrapy.Field()
    relationship_type = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    is_private = scrapy.Field()
    profile_pic = scrapy.Field()
    user_data = scrapy.Field()
    _id = scrapy.Field()
