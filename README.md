# ISB_ONLINE_ASSESSMENT

## Approach
### Step 1 Navigation to each fps 
1. Open the IMPDS portal:"https://impds.nic.in/sale/".
2. Selected the particular month and year
3. After that navigated to target state.
4. Retrieve all the active district of target state.
5. For each district performed following steps:
   * Open district page
   * Navigate to the FPS section
   * Collect the list of all available FPS IDs.
6. Iterate through each FPS by navigating to respective page, where the data for extraction resides.
7. Repeat the process until all FPSs in every active district have been processed for the selected month and year.

### Step 2 Failure and Retry Logic
Since the IMPDS website is dynamic and occasionally fails to load an FPS page correctly, a retry mechanism is implemented to improve scraping reliability.

### Failed FPS tracking
##### Maintained a list of dictionary (failed_fps) (structure : failed_fps = [ { "district": "NORTH GOA", "fps": "158500100001" } ])
Because, if the fps unable to load or an exception occurs during scraping, , append that fps and its distict to failed_fps.

### First pass 
  * Iterate through every district
  * Visit every FPS withing the district
  * Scrape the available data.
  * Record any failed FPS in failed_fps
### Second pass
  * Iterate through the failed_fps list
  * Retry scraping each failed FPS up to 2 additional times(Can be changed).
  * If FPS scrapped successful remove it from list.


## Hurdles

### 1. Dynamic Page Updates

Most of the pages are loaded dynamically using AJAX instead of a full page refresh. Because of this, explicit waits were required before interacting with elements or extracting data.

### 2. State and District Navigation

The website does not provide a direct list of districts. Active districts are shown as clickable markers on the state map, so the scraper first identifies these markers and then extracts the district names before navigating further.

### 3. Dynamic FPS Loading

Each FPS updates only the right-side panel without changing the URL. Proper synchronization was required to ensure that the updated data was loaded before scraping, preventing stale or incomplete data.

### 4. Expandable Commodity Table

The **Coarse Grains** section in the **Distributed Quantity (In Kg)** table is collapsed by default. The scraper expands this section before extracting the individual commodity values instead of only the aggregated total.

### 5. Failure and Retry Logic

Sometimes an FPS page does not load completely or throws an exception while scraping. Instead of stopping the entire pipeline, the failed FPS is added to a retry list and processed again after the first pass. This improves the overall scraping success rate.

### 6. Long Running Scraping Sessions

After scraping a large number of FPS pages continuously, the website occasionally becomes slow or stops responding. This is likely due to server-side request throttling or rate limiting.

A possible improvement is to introduce **adaptive request delays**, **exponential backoff**, and **proxy rotation** so that requests are distributed more evenly, making the scraper more reliable for long-running jobs.


## How to Run

### 1. Clone Repository
Open your terminal and run the following commands:
```bash
git clone [https://github.com/Vanshsehgal431/ISB_ONLINE_ASSESSMENT.git](https://github.com/Vanshsehgal431/ISB_ONLINE_ASSESSMENT.git)
cd ISB_ONLINE_ASSESSMENT

```
### 2. Activate virtual environment
```bash
  python -m venv venv
  venv\Scripts\activate
```

### 3. Install Dependencies
``` bash
pip install -r requirements.txt
```

### 4. Change Directory
```bash
cd pipeline

```

### 5. Running command
```bash
python run_pipeline.py

```

## Architecture 
## Architecture

The project follows a modular pipeline architecture where each module is responsible for a single task.

```text
                +----------------+
                |  browser.py    |
                | WebDriver Init |
                +-------+--------+
                        |
                        v
                +----------------+
                | navigator.py   |
                | Website        |
                | Navigation     |
                +-------+--------+
                        |
                        v
                +----------------+
                |  scraper.py    |
                | Data Extraction|
                +-------+--------+
                        |
                        v
                +----------------+
                |   writer.py    |
                | Raw CSV Writer |
                +-------+--------+
                        |
                        v
                data/raw/<month>/<district>/<fps>.csv
                        |
                        v
                +----------------------+
                | consolidate_data.py  |
                | Merge Raw CSV Files  |
                +----------+-----------+
                           |
                           v
                data/processed/fps-level-records-Goa.csv
```

### Module Responsibilities

* **browser.py** – Creates and configures the Selenium WebDriver.
* **navigator.py** – Handles navigation through Month → State → District → FPS.
* **scraper.py** – Extracts summary cards and all required transaction tables from an FPS page.
* **writer.py** – Stores each scraped FPS as an individual CSV in the raw data layer.
* **get_raw_data.py** – Orchestrates navigation, retry logic, scraping, and raw data generation.
* **consolidate_data.py** – Merges all raw CSV files into a single processed dataset.
* **logger.py** – Maintains execution logs for monitoring and debugging.
* **run_pipeline.py** – Entry point that executes the complete pipeline.

## Tech Stack

* **Language:** Python 3
* **Automation:** Selenium
* **Data Processing:** Pandas
* **Browser Driver:** ChromeDriver
* **Output Format:** CSV
* **Logging:** Python Logging Module


## Folder Structure

```text
ISB_ONLINE_ASSESSMENT/
│
├── sample_data/                      # Example or reference datasets
│   ├── data/
│   │   ├── raw/                      
│   │   │   ├── 03-2026/              
│   │   │   │   ├── NORTH GOA/        
│   │   │   │   │   └── 158500100001.csv
│   │   │   │   └── SOUTH GOA/
│   │   │   └── 04-2026/
│   │   │       ├── NORTH GOA/
│   │   │       │   └── 158500100001.csv
│   │   │       └── SOUTH GOA/
│   │   └── processed/                
│   │       └── fps-level-records-Goa.csv
│   ├── log/
│   │   └── scraper.log
│   ├── record_3-2026.json
│   └── record_4-2026.json
│
├── pipeline/                         # Source code and runtime output directory
│   ├── data/                         # Generated dynamically when running the pipeline
│   │   ├── raw/                      
│   │   │   ├── 03-2026/              
│   │   │   │   ├── NORTH GOA/        
│   │   │   │   │   └── 158500100001.csv
│   │   │   │   └── SOUTH GOA/
│   │   │   └── 04-2026/
│   │   │       ├── NORTH GOA/
│   │   │       │   └── 158500100001.csv
│   │   │       └── SOUTH GOA/
│   │   └── processed/                # Contains merged master dataset after consolidation
│   │       └── fps-level-records-Goa.csv
│   │
│   ├── log/                          # Generated runtime logs
│   │   └── scraper.log
│   │
│   ├── record_3-2026.json            # Generated tracking/state records
│   ├── record_4-2026.json
│   │
│   ├── get_raw_data.py               # Script to fetch/scrape raw data
│   ├── consolidate_data.py           # Script to merge and clean CSVs
│   ├── logger.py                     # Logging configuration
│   ├── run_pipeline.py               # Pipeline orchestrator (runs everything)
│   ├── navigator.py                  # Browser navigation helper
│   ├── browser.py                    # WebDriver configuration
│   ├── writer.py                     # Data output handler
│   ├── test.py                       # Test scripts
│   └── scraper.py                    # Main scraper logic
│
├── venv/                             # Local virtual environment
├── requirements.txt                  # Python dependencies (pandas, etc.)
└── README.md                         # Project documentation


```

