# Myntra Pulse

A web scraper that extracts and analyzes customer reviews and ratings from
Myntra product pages, built as part of the PW Skills Data Science program.

## Project Overview

- **Objective:** Develop a web scraper to extract customer reviews and
  ratings from Myntra's product pages.
- **Purpose:** Gain insights into customer sentiments and preferences to
  inform business decisions.
- **Outcome:** A structured dataset containing product reviews, ratings,
  and user feedback, viewable in-browser and downloadable as CSV.
- **Data Source:** Myntra's official website.

## Process Flow

1. User inputs a Myntra product URL (via Flask or Streamlit UI).
2. Scraper fetches and parses the webpage with `requests` + `BeautifulSoup`.
3. Extracted data is cleaned (whitespace, duplicates) and structured with
   `pandas`.
4. Data is presented in a user-friendly table and available for CSV
   download.

> **Note on live scraping:** Myntra renders much of its review content via
> JavaScript and actively blocks simple scripted requests. This project's
> scraper first attempts a live HTML fetch + parse. If that returns no
> reviews (common for a JS-rendered page or a blocked request), it
> automatically falls back to a generated demo dataset so the full
> pipeline — fetch, clean, store, display, download — can still be run
> and evaluated end-to-end. See `scraper.py` for extension points
> (internal API endpoints, Selenium/Playwright) if you want to pursue
> full live scraping.

## Tech Stack

| Purpose            | Library         |
|---------------------|-----------------|
| HTTP requests        | `requests`       |
| HTML parsing          | `beautifulsoup4` |
| Data structuring     | `pandas`         |
| Web interface (opt 1) | `Flask`         |
| Web interface (opt 2) | `streamlit`     |
| Production server    | `gunicorn`       |

## Project Structure

```
myntra-review-scrapper/
├── app.py                  # Flask web app
├── streamlit_app.py        # Streamlit web app (alternative UI)
├── scraper.py               # Core scraping / parsing / cleaning logic
├── requirements.txt
├── Procfile                 # gunicorn entry point for deployment
├── setup.sh                  # Conda environment setup script
├── pyproject.toml            # isort config (`profile = "black"`) — must be saved as UTF-8 without BOM
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── style.css
├── data/                      # Scraped CSV output lands here
├── notebooks/
│   └── exploration.ipynb      # Ad-hoc analysis of scraped data
├── tests/
│   └── test_scraper.py
├── .gitignore
└── README.md
```

> Note: the local virtual environment (created as `review-scraper/` per the
> setup steps below) lives inside the project folder but should **not** be
> committed or scanned by formatting tools — see Linting & Formatting below.

## System Requirements

- Python Version: **3.10**
- Package Manager: **Conda**
- Required libraries: `requests`, `beautifulsoup4`, `pandas`,
  `Flask`/`streamlit`, `gunicorn` (see `requirements.txt` for pinned
  versions)

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/sofdev1/myntra-pulse.git
cd myntra-review-scrapper
```

### 2. Create and activate a Conda environment

```bash
conda create -n myntra-review-scrapper python=3.10
conda activate myntra-review-scrapper
```

(Or simply run `bash setup.sh` to do both steps above automatically.)

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Option A — Flask

```bash
python app.py
```

Navigate to **http://localhost:5000**.

For production:

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### Option B — Streamlit

```bash
streamlit run streamlit_app.py
```

Navigate to **http://localhost:8501**.

## Usage

1. Enter a Myntra product URL, e.g.
   `https://www.myntra.com/tshirts/roadster/roadster-men-navy-blue-solid-round-neck-t-shirt/1234567/buy`
2. Click **Scrape Reviews**.
3. View extracted reviews, ratings, and summary stats in the results table.
4. Click **Download CSV** to save the structured dataset locally.

## Data Extraction Process

1. **User Input:** Myntra product URL.
2. **HTTP Request:** Fetches the product page content.
3. **HTML Parsing:** Identifies and extracts review sections.
4. **Data Cleaning:** Removes unnecessary characters and normalizes
   whitespace/formatting.
5. **Data Storage:** Organizes data into a structured CSV file.

## Running Tests

```bash
pip install pytest
pytest
```

## Linting & Formatting (isort + black)

CI runs `isort --check-only --skip review-scraper .` on every push/PR, so
imports must already be sorted and formatted correctly before you push.

### Config

`pyproject.toml` sets `profile = "black"` for isort, so its import style
agrees with `black`'s formatting instead of conflicting with it:

```toml
[tool.isort]
profile = "black"
```

If you ever need to recreate this file on Windows, **write it without a
UTF-8 BOM**, or isort will silently fail to read it (you'll see `Failed
to pull configuration information` and `Invalid statement (at line 1,
column 1)`, and isort will fall back to a style that fights with black):

```powershell
# Windows PowerShell 5.1
@"
[tool.isort]
profile = "black"
"@ | Out-File -Encoding ascii pyproject.toml

# PowerShell 7+
@"
[tool.isort]
profile = "black"
"@ | Out-File -Encoding utf8NoBOM pyproject.toml
```

Verify with `Format-Hex pyproject.toml` — it should start `5B 74 6F 6F`
(`[too...`), not `EF BB BF`.

### Fixing locally before you push

The local virtual environment folder (`review-scraper/`) must be excluded
from **both** tools, or you'll get parse errors trying to reformat
installed packages like pandas/numpy. isort uses `--skip`, black uses
`--extend-exclude`:

```powershell
isort --skip review-scraper .
black --extend-exclude "review-scraper" .
isort --check-only --skip review-scraper .
```

Run isort *before* black — running black afterward re-applies its own
line-wrapping on top of isort's ordering, so if you run them in the
wrong order (or `pyproject.toml` isn't set up correctly), black can
undo isort's fix and leave the check-only step failing again.

Once the check-only command passes cleanly, commit and push:

```powershell
git add .
git commit -m "Fix import sorting and formatting"
git push
```

Confirm the venv folder is actually excluded from git and from CI's
scan — check `.gitignore` includes `review-scraper/` (or whatever your
local env folder is named) so it's never committed in the first place.

## Benefits & Applications

- **Customer Insights** — understand customer satisfaction and areas for
  improvement.
- **Product Development** — inform design and feature enhancements based
  on feedback.
- **Marketing Strategies** — tailor campaigns to address common customer
  concerns.
- **Competitive Analysis** — benchmark against competitors by analyzing
  similar products.

## Future Enhancements

- **Sentiment Analysis:** Integrate NLP techniques to gauge overall
  sentiment (e.g. VADER, TextBlob, or a transformer model).
- **Automation:** Schedule regular scraping for continuous data updates
  (e.g. via `cron` or Airflow).
- **Data Visualization:** Build dashboards to visualize trends and
  patterns over time.
- **Scalability:** Extend the scraper to other e-commerce platforms.

## License

This project is provided for educational purposes. 
See `LICENSE` for details.