from urllib.parse import urlsplit, urljoin,urlparse
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import asyncio
import aiohttp
from aiohttp import ClientSession
from asyncio import Lock, Semaphore


class AsyncCrawler:
     def __init__(self, base_url:str, base_domain:str, max_concurrency:int):
        self.base_url = base_url
        self.base_domain = base_domain
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)

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

import requests
    

def crawl_page(base_url, current_url=None, page_data=None):

     if page_data is None:
        page_data = {}
        
     if current_url is None:
        current_url = base_url

     if urlparse(base_url).hostname != urlparse(current_url).hostname:
        return page_data

     print(type(current_url), repr(current_url))
     norm_url = normalize_url(current_url)

     if norm_url in page_data:
        return page_data

     print(f"Crawling: {norm_url}")
    
     try:
        html = get_html(current_url)
     except Exception as e:
        print(f"Skipping {current_url} due to error: {e}")
        return page_data 

     data = extract_page_data(html, current_url)
     page_data[norm_url] = data

     for link in data.get("outgoing_links", []): 
        crawl_page(base_url, link, page_data)

     return page_data

