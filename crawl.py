from urllib.parse import urlsplit, urljoin,urlparse
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import asyncio
import aiohttp
from aiohttp import ClientSession
from asyncio import Lock, Semaphore
import requests


class PageData(TypedDict):
     url: str
     heading: str
     first_paragraph: str
     outgoing_links: list[str]
     image_urls: list[str]
 
def normalize_url(url = None):
          parsed = urlsplit(url)
          normalized = (parsed.netloc + parsed.path).rstrip('/').lower()
          return normalized

def  get_heading_from_html(html:str) -> str:
          soup = BeautifulSoup(html,'html.parser')
          h_tag = soup.find('h1')
          if h_tag == None:
               h_tag = soup.find('h2')          
          return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
     soup = BeautifulSoup(html,'html.parser')
     m_tag = soup.find('main')
     if m_tag is not None and isinstance(m_tag, Tag):
          p_tag = m_tag.find('p')
     else:
          p_tag = soup.find('p')
     return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_urls_from_html(html, base_url):
     soup = BeautifulSoup(html,'html.parser')
     url_tags = soup.find_all('a')
     abs_urls = []
     for tag in url_tags:
         href = tag.get("href")
         if href is None:continue
         abs_urls.append(urljoin(base_url,href))
     return abs_urls

def get_images_from_html(html, base_url):
     soup = BeautifulSoup(html, 'html.parser')
     url_tags = soup.find_all('img')
     abs_urls = []
     for tag in url_tags:
          href = tag.get('src')
          if href is None:continue
          abs_urls.append(urljoin(base_url,href))
     return abs_urls

def extract_page_data(input_body, input_url):
     return {"url":input_url,
          "heading":get_heading_from_html(input_body),
          "first_paragraph":get_first_paragraph_from_html(input_body),
          "outgoing_links":get_urls_from_html(input_body,input_url),
          "image_urls":get_images_from_html(input_body, input_url)}   

async def crawl_site_async(base_url):
     crawler = AsyncCrawler(base_url)
     async with crawler:
          await crawler.crawl()
     return crawler.page_data
           

class AsyncCrawler:
     def __init__(self, base_url):
          self.base_url = base_url
          self.base_domain = urlsplit(base_url).netloc
          self.page_data = {}
          self.visited = set()
          self.lock = asyncio.Lock()
          self.max_concurrency = 10  # or whatever number you want, hardcoded here
          self.semaphore = asyncio.Semaphore(self.max_concurrency)
          self.session = None

     async def __aenter__(self):
          self.session = aiohttp.ClientSession()
          return self

     async def __aexit__(self, exc_type, exc_val, exc_tb):
          await self.session.close()

     async def add_page_visit(self, normalized_url):
          async with self.lock:
               if normalized_url in self.visited:
                   return False
               else:
                   self.visited.add(normalized_url)
                   return True

     async def get_html(self, url):
          async with self.session.get(url, headers = {"User-Agent": "BootCrawler/1.0"}) as response:
               response.raise_for_status()
               content_type = response.headers.get("Content-Type", "")
               if "text/html" not in content_type:
                    raise ValueError(f"Expected text/html content, but received: {content_type}")
               return await response.text()


     async def crawl_page(self, current_url:str):
          #domain filter
          if self.base_domain != urlsplit(current_url).netloc:
               return
          print(type(current_url), repr(current_url))
          normalized_url = normalize_url(current_url)
          # marking the url, no double visits!
          if not await self.add_page_visit(normalized_url):
               return
          #semaphore limited to network request
          async with self.semaphore:
               html = await self.get_html(current_url)       
          if html is None:
               return
          data = extract_page_data(html, current_url)
          #using the lock around shared state
          async with self.lock:
               self.page_data[normalized_url] = data
          tasks = []
          #create concurrent crawls and await them                         
          for link in data.get("outgoing_links", []): 
               tasks.append(asyncio.create_task(self.crawl_page(link)))
          if tasks:
               await asyncio.gather(*tasks, return_exceptions=True) 

     async def crawl(self):
          await self.crawl_page(self.base_url)
          return self.page_data
