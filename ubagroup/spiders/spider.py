import scrapy

from scrapy.loader import ItemLoader

from ..items import UbagroupItem
from itemloaders.processors import TakeFirst


class UbagroupSpider(scrapy.Spider):
	name = 'ubagroup'
	start_urls = ['https://www.ubagroup.com/media-centre/news/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="elementor-post__card"]')
		for post in post_links:
			url = post.xpath('.//h3[@class="elementor-post__title"]/a/@href').get()
			date = post.xpath('.//span[@class="elementor-post-date"]/text()[normalize-space()]').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@class="page-numbers next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1[@class="elementor-heading-title elementor-size-default"]/text()').get()
		description = response.xpath('//div[@class="elementor-text-editor elementor-clearfix"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=UbagroupItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
