import scrapy
import re
import requests
import cgi
from xml.sax.saxutils import unescape

class FlashApp(scrapy.Spider):
    name = "flash"
    allowed_domains = ['https://hooktheory.com']
    start_urls = ['https://www.hooktheory.com/theorytab/difficulties']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse)

    def parse(self, response):
        #yield scrapy.Request(url='https://www.hooktheory.com/theorytab/view/zun/fall-of-fall---autumnal-waterfall', callback=self._parse_data, dont_filter=True)
        href_links = response.xpath('//div[@class="row"]/div[contains(@class,"col-xs-4 text-right")]'
                                     '/h1[@class="tight"]/a/@href').extract()

        for href in href_links:
            url = 'https://www.hooktheory.com%s' % href

            yield scrapy.Request(url=url, callback=self._parse_all, dont_filter=True)

    def _parse_all(self, response):
        url_difficulty = response.url

        for i in range(1, 50):
            if "Next" in response.xpath('//div[@style="margin-bottom: 10px; margin-top: 10px;"]/a/text()').extract():
                href = url_difficulty + "?page={id}"
                href = href.format(id=i)
                yield scrapy.Request(url=href, callback=self._parse_pagenation, dont_filter=True)
            else:
                break
        href = url_difficulty + "?page={id}"
        href = href.format(id=i)
        yield scrapy.Request(url=href, callback=self._parse_pagenation, dont_filter=True)

    def _parse_pagenation(self, response):
        href_links = response.xpath('//ul[@class="grid246'
                                    '8"]/li[@class="grid-item"]/a/@href').extract()
        for href in href_links:
            url = 'https://www.hooktheory.com%s' % href
            yield scrapy.Request(url=url, callback=self._parse_data, dont_filter=True)

    def _parse_data(self, response):
        api_url = 'https://www.hooktheory.com/songs/getXmlByPk?pk={id}'

        song = response.xpath('//title/text()').extract()
        song = song[0].split(' by')[0]
        # Get data from "Verse Tag"
        if response.xpath('//div[contains(@id, "verse")]/div/@id'):
            verse_id = response.xpath('//div[contains(@id, "verse")]/div/@id').extract()
            api_verse = api_url.format(id=verse_id[0])
            data_verse = requests.get(url=api_verse).content

            if re.search('<notes>(.*)</notes>', data_verse, re.DOTALL):
                verse_notes = re.search('<notes>(.*)</notes>', data_verse, re.DOTALL).group()
            else:
                verse_notes = ''

            if re.search('<chords>(.*)</chords>', data_verse, re.DOTALL):
                verse_chords = re.search('<chords>(.*)</chords>', data_verse, re.DOTALL).group()
            else:
                verse_chords = ''

            # if re.search('<title>(.*)</title>', data_verse, re.DOTALL):
            #     song = re.search('<title>(.*)</title>', data_verse, re.DOTALL).group()
            # else:
            #     song = ''
        else:
            verse_notes = ''
            verse_chords = ''

        # Get data from "Chorus Tag"
        if response.xpath('//div[contains(@id, "chorus")]/div/@id'):
            chorus_id = response.xpath('//div[contains(@id, "chorus")]/div/@id').extract()
            api_chorus = api_url.format(id=chorus_id[0])
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

        # yield {
        #     'a': unescape(song, entities={"&lt;": "<", "&gt;": ">"}),
        #     'chorus_notes': unescape(chorus_notes),
        #     'chorus_chords': unescape(chorus_chords),
        #     'verse_notes': unescape(verse_notes),
        #     'verse_chords': unescape(verse_chords),
        # }