from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

class PageData(TypedDict):
     url: str
     heading: str
     first_paragraph: str
     outgoing_links: list[str]
     image_urls: list[str]

def normalize_url(self, url = None):
    if url == None:
         url = "http://www.boot.dev/blog/path/"
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

     
            


