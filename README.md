# Web Crawler

A powerful asynchronous web crawler built with Python that extracts content from websites and converts it to markdown format.

## Features

- 🚀 **Asynchronous crawling** with Playwright for JavaScript-rendered pages
- 📄 **Markdown conversion** of web content for easy processing
- 🎯 **Configurable depth** and URL patterns
- 🔍 **Smart content extraction** targeting main content areas
- 💾 **JSONL output** for easy data processing
- ⚙️ **YAML configuration** for easy customization
- 🛡️ **Rate limiting** to be respectful to target servers

## Requirements

- Python 3.7+
- Playwright browser binaries

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd webcrawler
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install chromium
```

## Configuration

Edit `config.yaml` to customize your crawl:

```yaml
base_url: "https://example.com"
max_depth: 3 # Maximum crawl depth
request_delay: 2.0 # Delay between requests (seconds)

start_paths: # Initial paths to crawl
  - "/"
  - "/about"
  - "/contact"

exclude_patterns: # URL patterns to skip
  - "/login"
  - "/admin"
  - "/images/"

output_file: "output/crawled_docs.jsonl"
```

### Configuration Options

- **base_url**: The base URL to crawl (required)
- **max_depth**: Maximum depth to follow links (0 = start URLs only)
- **request_delay**: Seconds to wait between requests (respect the server!)
- **start_paths**: List of paths to begin crawling from
- **exclude_patterns**: URL patterns to exclude from crawling
- **output_file**: Path to save the output JSONL file

## Usage

Run the crawler:

```bash
python main.py
```

The crawler will:

1. Load configuration from `config.yaml`
2. Start crawling from the specified URLs
3. Extract and convert content to markdown
4. Save results to the output JSONL file
5. Display progress and statistics

## Output Format

The crawler saves data in JSONL (JSON Lines) format. Each line is a JSON object:

```json
{
  "title": "Page Title",
  "headings": ["Heading 1", "Heading 2"],
  "content": "# Page Title\n\nMarkdown content...",
  "links": ["https://example.com/page1", "https://example.com/page2"],
  "url": "https://example.com/current-page",
  "depth": 1
}
```

### Fields

- **title**: The page title (from `<title>` tag)
- **headings**: List of all headings (h1-h4) found on the page
- **content**: Full page content converted to markdown
- **links**: List of internal links found on the page
- **url**: The URL of the crawled page
- **depth**: Crawl depth (0 for start URLs)

## How It Works

1. **Crawler initialization**: Sets up base URL, depth limits, and exclusion patterns
2. **Page fetching**: Uses Playwright to render JavaScript-heavy pages
3. **Content extraction**:
   - Removes scripts, styles, navigation, footers, and ads
   - Extracts main content area (targets `main`, `article`, or content divs)
   - Converts HTML to clean markdown
4. **Link discovery**: Finds and queues internal links for further crawling
5. **Breadth-first traversal**: Crawls level by level up to max depth
6. **Output**: Saves all extracted documents to JSONL format

## Code Structure

- `main.py`: Entry point, loads config and orchestrates the crawl
- `crawler.py`: Core crawler logic (NawalokaWebCrawler class)
- `config.yaml`: Configuration file
- `requirements.txt`: Python dependencies
- `output/`: Directory containing crawled data

## Customization

### Excluding Content

The crawler automatically excludes:

- Scripts, styles, navigation, footers, sidebars
- Binary files (images, PDFs, executables)
- JavaScript warning messages
- URLs matching exclude patterns

### Content Extraction

The crawler prioritizes content from:

1. `<div id="root">`
2. `<main>` tag
3. `<article>` tag
4. Divs with "content", "main", or "container" classes
5. `<body>` as fallback

## Tips

- Start with a small `max_depth` (1-2) to test configuration
- Use `request_delay` of at least 1-2 seconds to be respectful
- Check `robots.txt` before crawling any site
- Monitor output to ensure you're getting the content you want
- Adjust `exclude_patterns` to skip unwanted sections

## License

This project is provided as-is for educational and research purposes.

## Disclaimer

Always respect websites' `robots.txt` and terms of service. Use responsibly and ethically. Add appropriate delays between requests to avoid overwhelming servers.
