import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import sqlite3
import metadata_parser

sql = sqlite3.connect("sites.db")

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:

    def __init__(self, urls=[]):
        self.visited_urls = []
        self.urls_to_visit = urls

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find("title").text
        description = ""
        if soup.findAll("meta", attrs={"name": "description"}):
            description = soup.find("meta", attrs={"name": "description"}).get("content")
        h = requests.head(url)
        header = h.headers
        content_type = header.get('content-type')
        sql.execute(f"insert into sites (url, title, description) values ('{url}', '{title}', '{description}')")
        sql.commit()
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)

if __name__ == "__main__":
    Crawler(["https://"]).run()