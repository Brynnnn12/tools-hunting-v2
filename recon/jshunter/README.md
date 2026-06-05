# JSHunter

JavaScript intelligence framework — download, analyze, and extract endpoints from JS files.

**Author: [brynnnn12](https://github.com/brynnnn12) | Version: 1.0**

## Features

- Endpoint extraction (`/api`, `/graphql`, `/admin`, etc.)
- URL extraction (absolute URLs)
- GraphQL, WebSocket, storage reference detection
- Keyword discovery
- Source map detection
- Framework detection (React, Vue, Angular, Next.js, Nuxt, Webpack, Vite, jQuery)
- Reports: TXT, JSON, HTML (Bootstrap 5 dark theme)

## Installation

```bash
python -m venv .venv
# Linux/Mac: source .venv/bin/activate
# Windows:   .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python jshunter.py -h
python jshunter.py -u https://target.com/app.js
python jshunter.py -f js_urls.txt
python jshunter.py -f js_urls.txt --json --html
python jshunter.py -f js_urls.txt --threads 50
python jshunter.py -f js_urls.txt -o output/
python jshunter.py --version
```

## Output

```
output/target.com/
  endpoints.txt
  urls.txt
  graphql.txt
  websockets.txt
  storage.txt
  keywords.txt
  frameworks.txt
  sourcemaps.txt
  report.json
  report.html
```

## Project Structure

```
jshunter/
  jshunter.py   — CLI entrypoint
  core/         — config, logger, utils
  modules/      — downloader, extractor, classifier, reporter, statistics
  output/       — per-target results
  ```
