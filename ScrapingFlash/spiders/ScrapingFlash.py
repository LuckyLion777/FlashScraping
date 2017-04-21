import scrapy
import re
import requests
import cgi
from xml.sax.saxutils import unescape

class FlashApp(scrapy.Spider):
    name = "flash"

    allowed_domains = ['https://hooktheory.com']
    start_urls = ['https://www.hooktheory.com/theorytab/difficulties/intermediate?page=50']

    API_URL = 'https://www.hooktheory.com/songs/getXmlByPk?pk={id}'

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse)

    def parse(self, response):
        href_links = response.xpath('//ul[@class="grid2468"]/li[@class="grid-item"]/a/@href').extract()

        for href in href_links:
            url = 'https://www.hooktheory.com%s' % href
            yield scrapy.Request(url=url, callback=self.parse_data, dont_filter=True)

    def parse_data(self, response):
        song = response.xpath('//title/text()').extract()
        song = song[0].split(' by')[0]

        # Get data from "Verse Tag"
        if response.xpath('//div[contains(@id, "verse")]/div/@id'):
            verse_id = response.xpath('//div[contains(@id, "verse")]/div/@id').extract()
            api_verse = self.API_URL.format(id=verse_id[0])
            data_verse = requests.get(url=api_verse).content

            if re.search('<notes>(.*)</notes>', data_verse, re.DOTALL):
                verse_notes = re.search('<notes>(.*)</notes>', data_verse, re.DOTALL).group()
            else:
                verse_notes = ''

            if re.search('<chords>(.*)</chords>', data_verse, re.DOTALL):
                verse_chords = re.search('<chords>(.*)</chords>', data_verse, re.DOTALL).group()
            else:
                verse_chords = ''
        else:
            verse_notes = ''
            verse_chords = ''

        # Get data from "Chorus Tag"
        if response.xpath('//div[contains(@id, "chorus")]/div/@id'):
            chorus_id = response.xpath('//div[contains(@id, "chorus")]/div/@id').extract()
            api_chorus = self.API_URL.format(id=chorus_id[0])
            data_chorus = requests.get(url=api_chorus).content

            if re.search('<notes>(.*)</notes>', data_chorus, re.DOTALL):
                chorus_notes = re.search('<notes>(.*)</notes>', data_chorus, re.DOTALL).group()
            else:
                chorus_notes = ''

            if re.search('<chords>(.*)</chords>', data_chorus, re.DOTALL):
                chorus_chords = re.search('<chords>(.*)</chords>', data_chorus, re.DOTALL).group()
            else:
                chorus_chords = ''
        else:
            chorus_notes = ''
            chorus_chords = ''

        yield {
            'a': song,
            'chorus_notes': chorus_notes,
            'chorus_chords': chorus_chords,
            'verse_notes': verse_notes,
            'verse_chords': verse_chords,
        }
