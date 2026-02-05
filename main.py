import time
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from crawler import WebCrawler

def load_config():
    """Load configuration from YAML file."""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def run_threaded_crawler(config):
    """
    Executes the crawler in a separate thread to bypass 
    Jupyter's asyncio loop constraints.
    """
    c_cfg = config['crawler']
    
    # Construct full start URLs from paths
    base = c_cfg['base_url']
    start_urls = [base + path for path in c_cfg['start_paths']]
    
    crawler = WebCrawler(
        base_url=base,
        max_depth=c_cfg['max_depth'],
        exclude_patterns=c_cfg['exclude_patterns']
    )
    
    docs = crawler.crawl(start_urls, request_delay=c_cfg['request_delay'])
    return docs, crawler.visited

if __name__ == "__main__":
    # 1. Load settings
    config = load_config()
    
    print(f"🚀 Starting crawl at {time.strftime('%H:%M:%S')}...")
    start_time = time.time()

    # 2. Use ThreadPoolExecutor to isolate the Sync API from the main loop
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_threaded_crawler, config)
        documents, visited_urls = future.result()

    # Define output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Save as JSONL (Database format)
    jsonl_path = output_dir / "crawled_docs.jsonl"
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
    
    # 2. Save as Markdown (RAG format)
    for i, doc in enumerate(documents):
        # Create a safe filename from the URL
        safe_name = doc['url'].split('//')[1].replace('/', '_').replace(':', '')[:50]
        filename = f"{i:03d}_{safe_name}.md"
        
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(f"# {doc['title']}\n\n")
            f.write(f"**Source**: {doc['url']}\n\n")
            f.write(f"**Depth**: {doc['depth_level']}\n\n")
            f.write("---\n\n")
            f.write(doc['content'])

    print(f"\n✅ Successfully saved:")
    print(f"   - Corpus: {jsonl_path}")
    print(f"   - Markdown: {len(documents)} files in {output_dir}")
    
    # 3. Summary
    elapsed = time.time() - start_time
    print(f"\n✅ Crawl complete in {elapsed:.1f}s")
    print(f"📄 Documents collected: {len(documents)}")
    print(f"🔗 URLs visited: {len(visited_urls)}")