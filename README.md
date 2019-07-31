<h1>An Ebay-kleinanzeigen Web scraper using Python and Scrapy to fetch data into an ElasticSearch cluster with Kibana</h1>

The aim here is to extract data from https://www.ebay-kleinanzeigen.de/ automatically and rapidly in order to store them 
into an ElasticSearch cluster and get fast insights with Kibana.

<h2>Requirements</h2>
Python 3 <br/>
Elasticsearchb 7.0.2 <br/>
Scrapy 1.6.0 <br/>

<h2>How to set it :</h2>

1) Start your ElasticSearch cluster with Kibana installed on it. If you don't have it, a fast way to get it could be to install
and use a Docker image with the following steps :
```bash

git clone https://github.com/deviantony/docker-elk.git
cd /docker-elk
docker-compose up -d
```

2) Set the URLs (like https://www.ebay-kleinanzeigen.de/s-berlin/l3331 for example) you want to scrape in JSON file : start_urls.json
3) Set the various configuration parameters you wish :
```json
{
  "protocol": "http or https",
  "elastic_username": "the username to connect on your ElasticSearch cluster",
  "elastic_password": "the needed password to connect on your ElasticSearch cluster",
  "elastic_address": "the binded ip address of your ElasticSearch cluster",
  "elastic_port": "the binded port of your ElasticSearch cluster",
  "elastic_index_name": "the index name of your ElasticSearch cluster",
  "elastic_connection_retry": "the number of tries to reconnect on your ElasticSearch in case of failure",
  "scrape_next_pages": "boolean to indicate if the web scraper check the next pages (1,2,3...) displayed at the bottom of page."
}
```
The default login and server parameters of the ElasticSearch Docker images are entered.

4) Change your current directory to the Scraper's one and start it through :
```bash
cd .../ebaykleinanzeigen
scrapy crawl ebay_kleinanzeigen
```
5) The results are automatically updated into ElasticSearch and Kibana as soon as the data are being scraped.
Just enjoy the insights by connecting on your Kibana home page (by default in the Docker image : http://localhost:5601) !

NB: The number of concurrent requests and time between has been defined in settings.py respectively to 20 and 0.8 by default
in order to avoid problems on Ebay-kleinanzeigen's server.

<h2>References</h2>

-[Ebay-kleinanzeigen](https://www.ebay-kleinanzeigen.de/stadt/berlin/) <br/>
-[Elasticsearch-py](https://elasticsearch-py.readthedocs.io/en/master/) <br/>

<h2>Credits</h2>

Copyright (c) 2019, HicBoux. Work released under Apache 2.0 License. 

(Please contact me if you wish to use my work in specific conditions not allowed automatically by the Apache 2.0 License.)

<h2>Disclaimer</h2>

This solution has been made available for informational and educational purposes only. I hereby disclaim any and all 
liability to any party for any direct, indirect, implied, punitive, special, incidental or other consequential 
damages arising directly or indirectly from any use of this content, which is provided as is, and without warranties.
I also disclaim all responsibility for web scraping at a disruptive rate and eventual damages caused by a such use.
