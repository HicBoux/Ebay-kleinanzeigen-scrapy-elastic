import scrapy
import re
import json
from datetime import datetime
from elasticsearch import Elasticsearch
import logging
import time

class ElasticFunctions:

    def connection_to_elastic(self, connection_request, retry_number = 5):
	#We attempt to connect to Elastic several times until it works, otherwise we sent an error message
	es = Elasticsearch([connection_request], verify_certs=True)
        while(not es.ping() and i <= retry_number):
    		i+=1
	if not es.ping() : return ValueError("Connection failed")
	if es.ping() : return es

    def check_article_existence(self, elastic_client, index_name, doc_id):
	return elastic_client.exists(index=index_name, id=doc_id)
    
    def add_article_to_elastic(self, elastic_client, index_name, bulk_data, doc_id):
	if elastic_client.ping() :
		res = elastic_client.index(index=index_name, doc_type="article", id=doc_id, body=bulk_data)
		print("------------------------------ ", "Article added with : ", res["_shards"])
		elastic_client.indices.refresh()
	else: return "Not connected to Elastic."
