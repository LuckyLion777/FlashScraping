import scrapy
import re
import requests
import json
import xml.etree.cElementTree as ET
# from elementtree.SimpleXMLWriter import XMLWriter
import sys
import cgi
import os
# from xml.sax.saxutils import unescape
# from xml.dom.minidom import parseString

class FlashApp(scrapy.Spider):
    name = "flash"

    allowed_domains = ['https://hooktheory.com']
    start_urls = ['https://www.hooktheory.com/theorytab/difficulties/intermediate?page=50']
    # start_urls = ['https://www.hooktheory.com/theorytab/view/yuki-nagato/yuki-muon-madobe-nite']

    API_URL = 'https://www.hooktheory.com/songs/getXmlByPk?pk={id}'

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse)

    def parse(self, response):
        href_links = response.xpath('//ul[@class="grid2468"]/li[@class="grid-item"]/a/@href').extract()

        for href in href_links:
            url = 'https://www.hooktheory.com%s' % href
            yield scrapy.Request(url=url, callback=self.parse_data, dont_filter=True)

    def parse_data(self, response):
        i = 0
        categories = response.xpath('//div[@id="info"]//table[@class="table table-condensed"]'
                                    '//tbody//tr//td/text()').extract()
        for category in categories:
            if category == "Verse":
                verse_index = i
            if category == "Chorus":
                chorus_index = i
            i += 1

        # Get All Data in Verse Tag
        if response.xpath('//div[@id="verse"]/div/@id'):
            verse_id = response.xpath('//div[@id="verse"]/div/@id').extract()
            api_verse = self.API_URL.format(id=verse_id[0])
            verse_data = requests.get(url=api_verse).content
            # Get Title
            if re.search('<title>(.*)</title>', verse_data, re.DOTALL):
                song = re.search('<title>(.*)</title>', verse_data, re.DOTALL).group(1)
            else:
                song = ''

            # Get Category name
            category_name = response.xpath('//div[@id="info"]//table[@class="table table-condensed"]'
                                               '//tbody//tr//td/a/@href')[verse_index].extract()
            category_name = re.search('difficulties/(.*)', category_name, re.DOTALL).group(1)

            # Write data to file inside it's own directory
            if not os.path.exists(category_name):
                os.makedirs(category_name)

            with open(category_name + '/' + song + ".xml", 'w+') as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('%s\n %s\n %s\n' % ('<Verse_data>', verse_data, '</Verse_data>'))


        # Get All Data in Chorus Tag
        if response.xpath('//div[@id="chorus"]/div/@id'):
            chorus_id = response.xpath('//div[@id="chorus"]/div/@id').extract()
            api_chorus = self.API_URL.format(id=chorus_id[0])
            chorus_data = requests.get(url=api_chorus).content

            # Get Title
            if re.search('<title>(.*)</title>', chorus_data, re.DOTALL):
                song = re.search('<title>(.*)</title>', chorus_data, re.DOTALL).group(1)
            else:
                song = ''

            # Get Category name
            category_name = response.xpath('//div[@id="info"]//table[@class="table table-condensed"]'
                                           '//tbody//tr//td/a/@href')[chorus_index].extract()
            category_name = re.search('difficulties/(.*)', category_name, re.DOTALL).group(1)

            # Write data to file inside it's own directory
            if not os.path.exists(category_name):
                os.makedirs(category_name)

            with open(category_name + '/' + song + ".xml", 'w+') as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('%s\n %s\n %s\n' % ('<Chorus_Data>', chorus_data, '</Chorus_Data>'))