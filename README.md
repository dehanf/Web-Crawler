Web Crawler 🏥

A robust, RAG-ready web crawler designed to extract content from websites. It handles dynamic JavaScript (SPA) content and converts pages into clean Markdown and JSONL formats suitable for LLM embedding.

## 🌟 Key Features

- **Windows & Jupyter Compatible:** Uses a threaded bridge to bypass `NotImplementedError` and event loop conflicts common on Windows.
- **SPA Support:** Uses Playwright to render JavaScript and wait for dynamic React components to load.
- **Clean Data Extraction:** Automatically removes navigation, footers, scripts, and **Base64 encoded images** to prevent noise in your vector database.
- **Configurable:** distinct settings for depth, exclusion patterns, and starting paths via `config.yaml`.

## 📂 Project Structure

```text
.
├── config.yaml       # Configuration file (URLs, depth, exclusions)
├── crawler.py        # Core logic: Playwright Sync API & BeautifulSoup
├── main.py           # Execution script (runs crawler in a background thread)
├── requirements.txt  # Python dependencies
└── output/           # Generated .md and .jsonl files

🛠️ Installation & Setup
1. Install Python Dependencies
pip install -r requirements.txt

2. Install Browser Binaries
Playwright needs browser binaries to function. Even if you have Chrome installed, you must run this command:

playwright install chromium

3. Configure the Crawler
Ensure your config.yaml has the correct structure (indented under crawler:):

🚀 Usage
Run the crawler using the main script. Do not run crawler.py directly; main.py handles the necessary threading logic.
python main.py

Output:
Markdown Files (*.md): Saved in output/ (or configured path). Contains the cleaned text content, headings, and metadata.

JSONL Corpus (*.jsonl): A single file containing structured data (URL, depth, links, content) for all crawled pages.
```
