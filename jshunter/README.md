# JSHunter

JSHunter adalah framework analisis JavaScript untuk bug bounty, pentesting, dan asset discovery yang membantu security researcher memahami attack surface aplikasi web dengan menganalisis file JavaScript.

## Features

- Endpoint extraction untuk path penting seperti `/api`, `/graphql`, `/admin`, dan lain-lain
- URL extraction untuk URL absolut
- GraphQL, WebSocket, storage reference detection
- Keyword discovery untuk kata kunci menarik
- Source map detection
- Framework detection (React, Vue, Angular, Next.js, Nuxt, Webpack, Vite, jQuery)
- Statistik ringkas dan report JSON/HTML

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python jshunter.py -h
python jshunter.py -u https://target.com/app.js
python jshunter.py -f js.txt
python jshunter.py -f js.txt --json
python jshunter.py -f js.txt --html
python jshunter.py -f js.txt --threads 50
python jshunter.py -f js.txt --output output/
```

## Screenshots

- Placeholder for CLI screenshot
- Placeholder for report HTML screenshot

## Project Structure

```
jshunter/
  jshunter.py
  core/
  modules/
  output/
  reports/
  logs/
```

## Output Examples

```
output/
└── target.com/
    ├── endpoints.txt
    ├── urls.txt
    ├── graphql.txt
    ├── websockets.txt
    ├── storage.txt
    ├── keywords.txt
    ├── frameworks.txt
    ├── sourcemaps.txt
    ├── report.json
    └── report.html
```

## Roadmap v2

- JavaScript AST Analysis
- Source Map Parsing
- Entropy Analysis
- API Discovery Engine
- Technology Fingerprinting
