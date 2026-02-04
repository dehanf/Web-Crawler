import re
import asyncio
from typing import List, Dict, Any, Set
from collections import deque
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

class WebCrawler:
    def __init__(self, base_url: str, max_depth: int, exclude_patterns: List[str]):
        self.base_url = base_url.rstrip('/')
        self.max_depth = max_depth
        self.exclude_patterns = exclude_patterns
        self.visited: Set[str] = set()
        self.documents: List[Dict[str, Any]] = []

    def should_crawl(self, url: str) -> bool:
        if url in self.visited or not url.startswith(self.base_url):
            return False
        for pattern in self.exclude_patterns:
            if pattern in url: return False
        if re.search(r'\.(jpg|jpeg|png|gif|pdf|zip|exe)$', url, re.I):
            return False
        return True

    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        for element in soup(["script", "style", "nav", "footer", "aside", "noscript", "iframe"]):
            element.decompose()
        
        title = (soup.title.string if soup.title else url.split("/")[-1]) or "Untitled"
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4'])]
        
        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a.get('href', ''))
            href = href.split('#')[0].split('?')[0].rstrip('/')
            if href.startswith(self.base_url) and href != url:
                links.append(href)

        main_content = (
            soup.find('div', {'id': 'root'}) or 
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', {'class': re.compile('content|main|container', re.I)}) or
            soup.body
        )
        
        content_md = md(str(main_content), heading_style="ATX") if main_content else md(str(soup), heading_style="ATX")
        content_md = re.sub(r'You need to enable JavaScript.*?\.', '', content_md, flags=re.IGNORECASE)
        content_md = re.sub(r'\n{3,}', '\n\n', content_md).strip()
        
        return {
            "title": title.strip(),
            "headings": headings,
            "content": content_md,
            "links": list(set(links))
        }

    async def crawl_async(self, start_urls: List[str], request_delay: float = 2.0):
        queue = deque([(url, 0) for url in start_urls])
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            while queue:
                url, depth = queue.popleft()
                if depth > self.max_depth or not self.should_crawl(url):
                    continue
                
                try:
                    print(f"🔍 [{depth}] Crawling: {url}")
                    self.visited.add(url)
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(2) # Buffer for JS
                    
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    doc_data = self.extract_content(soup, url)
                    doc_data.update({"url": url, "depth": depth})
                    
                    if len(doc_data['content']) >= 100:
                        self.documents.append(doc_data)
                        if depth < self.max_depth:
                            for link in doc_data['links']:
                                if link not in self.visited:
                                    queue.append((link, depth + 1))
                    
                    await asyncio.sleep(request_delay)
                except Exception as e:
                    print(f"❌ Error {url}: {str(e)[:50]}")
            
            await browser.close()
        return self.documents