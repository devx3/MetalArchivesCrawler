import json
import time
from typing import Dict, List

import scrapy
import string
import logging
import re
import requests
from bs4 import BeautifulSoup

from core.items import MetalArchiveItem

logger = logging.getLogger()

START_URL_FMT = (
    'http://www.metal-archives.com/browse/ajax-letter/l/{letter}/json/1?'
    'sEcho=1&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=500'
    '&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=0&'
    'sSortDir_0=asc&iSortingCols=1&bSortable_0=true&bSortable_1=true&'
    'bSortable_2=true&bSortable_3=false&_={time}'
)

NEXT_URL_FMT = (
    'http://www.metal-archives.com/browse/ajax-letter/l/{letter}/json/1?'
    'sEcho=1&iColumns=4&sColumns=&iDisplayStart={start}&iDisplayLength=500'
    '&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&iSortCol_0=0&'
    'sSortDir_0=asc&iSortingCols=1&bSortable_0=true&bSortable_1=true&'
    'bSortable_2=true&bSortable_3=false&_={time}'
)

DISCOGRAPHY_URL_FMT = (
    'https://www.metal-archives.com/band/discography/id/{band_id}/tab/all'
)


class MetalArchivesSpider(scrapy.Spider):
    name = 'metal-archives'
    allowed_domains = ['www.metal-archives.com']

    def start_requests(self):
        letters = [letter for letter in string.ascii_lowercase] + ['NBR']

        # TODO: Voltar a usar a lista acima
        for letter in letters:
            url = START_URL_FMT.format(letter=letter, time=int(time.time()))
            meta = {'letter': letter}
            yield scrapy.Request(url, callback=self.parse_bands, meta=meta)

    def parse_bands(self, response):
        data = json.loads(response.body)
        total = data['iTotalRecords']
        for i in range(0, total, 500):
            url = NEXT_URL_FMT.format(letter=response.meta['letter'], start=i, time=time.time())
            yield scrapy.Request(url, callback=self.parse_json)

    def parse_json(self, response):
        data = json.loads(response.body)
        for band in data['aaData']:
            url = self._extract_band_link(band[0])
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        band_id = self._get_band_id(response.url)
        data = {
            'band_id': band_id,
            'band_name': response.xpath('//h1[@class="band_name"]/a/text()').extract_first(),
            'country_of_origin': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Country of origin")]/following-sibling::dd/a/text()'
            ).extract_first(),
            'location': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Location")]/following-sibling::dd/text()'
            ).extract_first(),
            'status': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Status")]/following-sibling::dd/text()'
            ).extract_first(),
            'formed_in': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Formed in")]/following-sibling::dd/text()'
            ).extract_first(),
            'years_active': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Years active")]/following-sibling::dd/text()'
            ).extract_first(),
            'genre': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Genre")]/following-sibling::dd/text()'
            ).extract_first(),
            'lyrical_themes': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Lyrical themes")]/following-sibling::dd/text()'
            ).extract_first(),
            'current_label': response.xpath(
                '//*[@id="band_stats"]//dt[contains(text(), "Current label")]/following-sibling::dd/a/text()'
            ).extract_first(),
            'band_logo': response.xpath('//*[contains(@class, "band_name_img")]/a/img/@src'
                                        ).extract_first(),
            'band_img': response.xpath('//*[contains(@class, "band_img")]/a/img/@src'
                                       ).extract_first(),
            'band_albums': self._get_discography(DISCOGRAPHY_URL_FMT.format(band_id=band_id)),
            'band_members': self._get_members(response),
        }
        item = MetalArchiveItem(
            **data
        )

        yield item

    @staticmethod
    def _get_members(response) -> List[Dict[str, str]]:
        trs = response.xpath('//*[contains(@class, "lineupTable")]/tr[@class="lineupRow"]')

        members = []
        for tr in trs:
            member_name = tr.xpath('./td[1]/a/text()').extract_first()
            instrument = tr.xpath('./td[2]/text()').extract_first()
            members.append({
                "member_name": member_name,
                "instrument": instrument
            })
        return members

    @staticmethod
    def _get_discography(url) -> List[Dict[str, str]]:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        trs = soup.select('table tbody tr')

        albums = []
        for tr in trs:
            try:
                album_name = tr.find('a').text
                album_type = tr.select('td:nth-child(2)')[0].text
                album_year = tr.select('td:nth-child(3)')[0].text
                albums.append({
                    'album_name': album_name,
                    'album_type': album_type,
                    'album_year': album_year,
                })
            except AttributeError:
                pass

        return albums

    @staticmethod
    def _get_band_id(url):
        """Parse from URL the band id"""
        url = url.split('/')[-1]
        return url

    @staticmethod
    def _extract_band_link(raw_link):
        regex = re.compile(".*href='(.*)'.*")
        link = regex.match(raw_link)
        return link.group(1)
