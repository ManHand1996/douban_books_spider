# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Identity, Join,TakeFirst
from w3lib.html import remove_tags

def clean_book_name(value):
    result = value.strip("\n '")
    if result != "":
        return result

def clean_book_info(value):
    result = remove_tags(value).strip(' \n')
    if result != "":
        return result
    else:
        return "unknow/unknow/unknow/unknow/unknow"

def replace_empty_comments(value):
    tmp = remove_tags(value).strip(' \n')
    if tmp == '(少于10人评价)' or tmp == '(目前无人评价)':
        return '0.0'

    r = remove_tags(value).strip(' \n(少于目前暂无人评价)')
    if r == '' or len(r) == 0:
        return '0.0'
    else:
        return r

def replace_empty_ratings(value):
    r = remove_tags(value)
    if r == '' or len(r) == 0:
        return '0'
    else:
        return r

class BookItem(Item):
    """docstring for myItem"""
    book_name = Field(
        input_processor = MapCompose(clean_book_name),
        output_processor = TakeFirst(),
    )
    
    book_info = Field(
        input_processor = MapCompose(clean_book_info),
        output_processor = TakeFirst(),
    )

    rating = Field(
        input_processor = MapCompose(replace_empty_ratings),
        output_processor = TakeFirst(),
    )

    comments = Field(
        input_processor = MapCompose(replace_empty_comments),
        output_processor = TakeFirst(),
    )

    tag = Field()

class MyItemLoader(ItemLoader):
    default_item_class = BookItem
    default_input_processor = MapCompose()
    default_output_processor = TakeFirst()
    description_out = Join()
