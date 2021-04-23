import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BnzItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BnzSpider(scrapy.Spider):
	name = 'bnz'
	start_urls = ['https://blog.bnz.co.nz/category/media-updates']

	def parse(self, response):
		post_links = response.xpath('//div[@class="col"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="post-date mb-3"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BnzItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
