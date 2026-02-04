import yaml
import asyncio
import json
import os
import time
from crawler import WebCrawler

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

async def main():
    cfg = load_config()
    os.makedirs(os.path.dirname(cfg['output_file']), exist_ok=True)

    # Prepare start URLs
    start_urls = [cfg['base_url'].rstrip('/') + path for path in cfg['start_paths']]

    crawler = NawalokaWebCrawler(
        base_url=cfg['base_url'],
        max_depth=cfg['max_depth'],
        exclude_patterns=cfg['exclude_patterns']
    )

    print(f"🚀 Starting crawl on {cfg['base_url']}...")
    start_time = time.time()
    
    results = await crawler.crawl_async(start_urls, cfg['request_delay'])

    # Save to JSONL
    with open(cfg['output_file'], 'w', encoding='utf-8') as f:
        for doc in results:
            f.write(json.dumps(doc) + '\n')

    print(f"\n✅ Done! Saved {len(results)} docs to {cfg['output_file']}")
    print(f"⏱️ Time elapsed: {time.time() - start_time:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())