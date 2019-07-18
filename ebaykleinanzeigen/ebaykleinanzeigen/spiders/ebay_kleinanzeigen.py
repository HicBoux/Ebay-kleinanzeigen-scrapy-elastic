# -*- coding: utf-8 -*-
import scrapy
import re
import json
import logging
from datetime import datetime

from elasticsearch import Elasticsearch

from ebaykleinanzeigen.spiders.utilities import Utilities
from ebaykleinanzeigen.spiders.elastic_functions import ElasticFunctions

class EbayKleinanzeigenSpider(scrapy.Spider):
    name = 'ebay_kleinanzeigen'
    allowed_domains = ['ebay-kleinanzeigen.de']

    def __init__(self, *args, **kwargs):
	#Load home made classes with functions
	self.utilities = Utilities()
	self.elastic_functions = ElasticFunctions()

	#Load of configuration files
        self.start_urls = self.utilities.load_urls("start_urls.json")
	self.config = self.utilities.load_config_file("config_file.json")

	#Connection to ELK
	connection_request = self.config["protocol"] + "://" + self.config["elastic_username"] + ":" + self.config["elastic_password"] + "@" + self.config["elastic_address"] + ":" + self.config["elastic_port"]
	self.es = self.elastic_functions.connection_to_elastic(connection_request, self.config["elastic_connection_retry"])
	

    def parse(self, response):
	article_urls = response.xpath("//a[@class='ellipsis']/@href").extract()
	for url in article_urls:
		domain = 'https://www.ebay-kleinanzeigen.de'
		article_page = response.urljoin(domain + url)
		print(article_page)
		request = scrapy.Request(url = article_page, callback=self.parse_article_page, dont_filter=True)
		yield request
	
	next_page = domain + str(response.xpath("//a[@class='pagination-next']/@href").extract_first())
	print(next_page)
	if next_page is not None and self.config["scrape_next_pages"] == "True": #If still some next pages to follow and if it's agreed in the config
		yield scrapy.Request(
		response.urljoin(next_page),
		callback=self.parse)

    def parse_article_page(self, response):
	
	#Retrieve some data about the article
	article_url = response.url
	article_title = response.xpath("//h1[@class='articleheader--title']//text()").extract_first()
	article_price = [s[7:] for s in response.xpath("//h2[@class='articleheader--price']//text()").extract()][0]
	article_description = response.xpath("//p[@itemprop='description']").extract_first()
	article_description = re.compile(r'<[^>]+>').sub('', article_description).split(" ").remove('') #Remove all HTML elements in order to have only one text block

	#Retrieve all data categories about the product ("type", "size", "delivery way" etc...)
	article_details_categories = [s.replace(":","") for s in response.xpath("//dt[@class='attributelist--key']//text()").extract()]

	#Retrieve the place where the article is sold
	seller_place = [s.strip() for s in response.xpath("//dd[@class='attributelist--value' and  @itemprop='seller']//text()").extract()]
	seller_place = ''.join(seller_place)

	#Retrieve all data (values) about the product ("2m", "Man" etc...)
	article_details_values = list(filter(None, [s.strip() for s in response.xpath("//dd[@class='attributelist--value' and not(@itemprop='seller')]//text()").extract()]))
	#Add the seller place to the list
	article_details_values.insert(0, seller_place)
	if ',' in article_details_values : article_details_values.remove(',') #Remove useless cells
	#Since some fields (like "Ausstatung" or "Art") have several values, we try to merge them into a given field
	len_cat = len(article_details_categories)
	len_val = len(article_details_values)
	article_details_values[len_cat-1] = article_details_values[len_cat-1] + ' ' #Avoid the first ending values to not be taken into account
	article_details_values[len_cat-1 : len_val] = [' '.join(article_details_values[len_cat-1 : len_val]).replace(",","")] #Merge all ending values
	article_details_values[len(article_details_values)-1] = filter(None, article_details_values[len(article_details_values)-1].split("  ")) #Remove empty cells and split values
	#In the case there is only 1 field, we transform this list into a simple String
	if len(article_details_values[len(article_details_values)-1]) == 1 : article_details_values[len(article_details_values)-1] = article_details_values[len(article_details_values)-1][0]

	#Definition of the dict to return to ELK
	article = []
	article.append(("URL", article_url))
	article.append(("Artikelstitel", article_title))
	article.append(("Preis", article_price))
	for i in range(len(article_details_categories)): 
	    article.append((article_details_categories[i], article_details_values[i]))
	article.append(("Artikelsbeschreibung", article_description))
	article = dict(article) #Transformation into a dictionary
	doc_id = article["URL"].split("/")[5] #Get the article's ID available in the URL

	#Transform possible values into float or dates
	article = self.utilities.infer_data_types(article)


	#Push the article into ELK : if and only if the document doesn't exist already in the index
	if not self.elastic_functions.check_article_existence(self.es, self.config["elastic_index_name"], doc_id):
		self.elastic_functions.add_article_to_elastic(self.es, self.config["elastic_index_name"], article, doc_id)
	else : print("-------------------------------- Article already indexed in Elastic.")

	yield article
    	

