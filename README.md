# ISB_ONLINE_ASSESSMENT

## How to Run

### 1. Clone Repository
Open your terminal and run the following commands:
```bash
git clone [https://github.com/Vanshsehgal431/ISB_ONLINE_ASSESSMENT.git](https://github.com/Vanshsehgal431/ISB_ONLINE_ASSESSMENT.git)
cd ISB_ONLINE_ASSESSMENT

```
### 2. Change Directory
```bash
cd pipeline

```
### 3. Activate virtual environment

### 4. Running command
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
