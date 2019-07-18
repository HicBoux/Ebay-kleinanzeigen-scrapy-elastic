import scrapy
import re
import json
from datetime import datetime
from elasticsearch import Elasticsearch
import logging
import time

class Utilities:

    def load_urls(self, filename = "start_urls.json"):
        with open('start_urls.json') as file:
            links = json.load(file)
            return links['urls']

    def load_config_file(self, filename = "config_file.json"):
        with open('config_file.json') as file:
            config = json.load(file)
            return config

    def is_int(self, value):
	try:
		int(str(value))
		return True
	except ValueError:
		return False

    def is_float(self, value):
	try:
		float(str(value))
		return True
	except ValueError:
		return False

    def is_date(self, value):
	try:
    		datetime.strptime(str(value), '%d.%m.%Y')
		return True
	except ValueError:
    		return False

    def infer_data_types(self, article):
	for key in article:
		if isinstance(article[key], list): continue 
		elif self.is_int(article[key]): article[key] = int(article[key])
		elif self.is_float(article[key]): article[key] = float(article[key])
		elif self.is_date(article[key]) and str(article[key]) is not None: article[key] = datetime.strptime(str(article[key]), '%d.%m.%Y')
	return article

