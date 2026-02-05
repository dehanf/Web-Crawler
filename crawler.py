from typing import List, Dict, Any, Set
from collections import deque
import re
import time
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

class WebCrawler:
    """
    Synchronous web crawler using Playwright for JavaScript-rendered content.
    """
    
    def __init__(self, base_url: str, max_depth: int, exclude_patterns: List[str]):
        self.base_url = base_url
        self.max_depth = max_depth
        self.exclude_patterns = exclude_patterns
        self.visited: Set[str] = set()
        self.documents: List[Dict[str, Any]] = []
    
    def should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled based on rules."""
        if url in self.visited:
            return False
        if not url.startswith(self.base_url):
            return False
        for pattern in self.exclude_patterns:
            if pattern in url:
                return False
        # Skip media files to save bandwidth
        if re.search(r'\.(jpg|jpeg|png|gif|pdf|zip|exe)$', url, re.I):
            return False
        return True
    
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract clean content from HTML soup and remove Base64 noise."""
        # Remove noise elements
        for element in soup(["script", "style", "nav", "footer", "aside", "noscript", "iframe"]):
            element.decompose()
        
        # Remove Base64 encoded images to keep markdown clean
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src.startswith('data:image'):
                img.decompose()
        
        title = soup.title.string if soup.title else url.split("/")[-1]
        title = title.strip() if title else "Untitled"
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3', 'h4'])]
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if not href: continue
            if href.startswith('/'):
                href = self.base_url + href
            elif not href.startswith('http'):
                href = urljoin(url, href)
            
            if href.startswith(self.base_url):
                href = href.split('#')[0].split('?')[0]
                if href and href != url:
                    links.append(href)
        
        # Target main content areas for better RAG quality
        main_content = (
            soup.find('div', {'id': 'root'}) or 
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', {'class': re.compile('content|main|container', re.I)}) or
            soup.body
        )
        
        content_md = md(str(main_content), heading_style="ATX") if main_content else md(str(soup), heading_style="ATX")
        # Remove JS-required warnings from output
        content_md = re.sub(r'You need to enable JavaScript.*?\.', '', content_md, flags=re.IGNORECASE)
        content_md = re.sub(r'\n{3,}', '\n\n', content_md).strip()
        
        return {
            "title": title,
            "headings": headings,
            "content": content_md,
            "links": list(set(links))
        }

    def crawl(self, start_urls: List[str], request_delay: float = 2.0) -> List[Dict[str, Any]]:
        """
        Synchronous BFS crawl using Playwright Sync API.
        """
        queue = deque([(url, 0) for url in start_urls])
        
        with sync_playwright() as p:
            # Launch Chromium (ensure 'playwright install chromium' was run)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)
            
            while queue:
                url, depth = queue.popleft()
                if depth > self.max_depth or not self.should_crawl(url):
                    continue
                
                try:
                    print(f"🔍 [{depth}] {url}")
                    self.visited.add(url)
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    
                    # Wait for SPA/React rendering
                    try:
                        page.wait_for_selector("body", timeout=10000)
                        page.wait_for_timeout(3000) 
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1000)
                    except:
                        page.wait_for_timeout(5000)
                    
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    doc_data = self.extract_content(soup, url)
                    doc_data['url'] = url
                    doc_data['depth_level'] = depth
                    
                    if len(doc_data['content']) >= 100:
                        self.documents.append(doc_data)
                        print(f"   ✅ Saved ({len(doc_data['content'])} chars)")
                    
                    if depth < self.max_depth:
                        for link in doc_data['links']:
                            if link not in self.visited and link not in [item[0] for item in queue]:
                                queue.append((link, depth + 1))
                    
                    # Respect site with request delay
                    time.sleep(request_delay)
                except Exception as e:
                    print(f"   ❌ Error crawling {url}: {str(e)[:100]}")
                    continue
            
            browser.close()
        return self.documents