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

#### Failed FPS tracking
##### Maintained a list of dictionary (failed_fps) (structure : failed_fps = [ { "district": "NORTH GOA", "fps": "158500100001" } ])
Because, if the fps unable to load or an exception occurs during scraping, , append that fps and its distict to failed_fps.

#### First pass iterate over each fps in each district for particular month and year.
#### Second pass with 2 retry logic(can be increased), i.e. Iterate over the list(failed_fps) two times so that every fps data get extracted.


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

