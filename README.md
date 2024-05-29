# dark-market-scout
This repository hosts the code for our project for the course Data Forensics at JADS. 

---

## Repository Structure

The repository is organized into several directories and files, each serving a specific purpose in the project. Below is a brief overview of the main components:

```
.
├── requirements.txt
├── config
├── crawler
├── tests
├── resources
├── scraper
└── dashboard
```

### Description of Main Components

- **requirements.txt**: Lists the Python dependencies required for the project.
- **config**: Contains configuration files and settings used throughout the project.
- **crawler**: Includes scripts and modules for web crawling, focusing on detecting and handling CAPTCHAs.
- **tests**: Includes test cases and sample data to verify that the CAPTCHA detector is functioning correctly.
- **resources**: This directory stores the raw crawled pages.
- **scraper**: Contains scripts for scraping data from web pages, including specific scripts for different websites and logs of the scraping process.
- **dashboard**: Contains files and resources for the project's dashboard, which is to be added later for visualizing data and results.

---

## Installation requirements
1. Create a virtual environment
1. Run the requirements: `pip install -r requirements.txt` 
2. Then install the command line version of the TOR browser on your machine:
   * on Mac OS: `brew install tor` & `brew services start tor`
   * on Linux: `apt-get install tor` &  `service tor start`

---

### Crawler

The `crawler` module is responsible for navigating and collecting data from various web sources, particularly focusing on detecting and handling CAPTCHA challenges. The structure of the `crawler` module is as follows:

```
crawler/
├── __init__.py
├── captcha
│   ├── __init__.py
│   ├── detector.py
│   └── training-data
│       ├── captcha
│       ├── detected
│       └── non_captcha
├── crawler.py
├── runner.py
└── torcontrol.py
```

#### Files and Directories

- `__init__.py`: Initializes the `crawler` module.
- `captcha/`: Contains components related to CAPTCHA detection.
  - `__init__.py`: Initializes the `captcha` submodule.
  - `detector.py`: Hold the sourcecode for the Captcha Detector that is being used by the Crawler.
  - `training-data/`: Directory containing training data for CAPTCHA detection.
    - `captcha/`: Training data classified as CAPTCHA.
    - `detected/`: Data detected as CAPTCHA during crawling.
    - `non_captcha/`: Training data classified as non-CAPTCHA.
- `crawler.py`: Main script for crawling web data.
- `runner.py`: The main script to execute crawler, must be configured for the marketplace that is being crawled.
- `torcontrol.py`: Handles TOR network control by requesting a new random circuit of union routers every 30 seconds.

---

### Tests

The `tests` directory is responsible for verifying that the CAPTCHA detector is correctly configured and effectively identifies CAPTCHAs from the marketplaces being scraped. The structure of the `tests` directory is as follows:

```
tests/
├── __init__.py
├── conftest.py
├── data
│   ├── captcha
│   └── non_captcha
└── test_captcha_detector.py
```

#### Files and Directories

- `__init__.py`: Initializes the `tests` module.
- `conftest.py`: Configuration file for pytest. It can be used to define fixtures and other configurations for the test suite.
- `data/`: Directory containing sample data for testing the CAPTCHA detector.
  - `captcha/`: Contains sample data that should be detected as CAPTCHAs.
  - `non_captcha/`: Contains sample data that should not be detected as CAPTCHAs.
- `test_captcha_detector.py`: Contains test cases for the CAPTCHA detector.

#### Usage

1. **Running the Tests:**

    Use pytest to run the test suite. This will execute the test cases defined in `test_captcha_detector.py` and ensure that the CAPTCHA detector is working correctly.

    ```sh
    pytest
    ```

2. **Sample Data for Testing:**

    The `data` directory contains sample HTML files used to test the CAPTCHA detector.
    
    - `captcha/`: This directory contains HTML files that are known to include CAPTCHAs. The test cases will verify that these files are correctly identified as containing CAPTCHAs.
    - `non_captcha/`: This directory contains HTML files that do not include CAPTCHAs. The test cases will ensure that these files are not falsely identified as containing CAPTCHAs.

---

### Scraper

The `scraper` module is responsible for extracting specific information from the web pages that are crawled. It includes scripts tailored to different websites and logs for monitoring the scraping process. The structure of the `scraper` module is as follows:

```
scraper/
├── __init__.py
├── generic.py
├── logs
├── nexus.py
├── scraped
│   └── cleaned
│       └── cleaning.ipynb
└── wtn.py
```

#### Files and Directories

- `__init__.py`: Initializes the `scraper` module.
- `generic.py`: Contains generic scraping class that can be reused across different scraping scripts.
- `wtn.py`: Script specifically for scraping data from the We The North website.
- `nexus.py`: Script specifically for scraping data from the Nexus website.
- `logs/`: Directory containing logs of the scraping process.
- `scraped/`: Directory containing scraped data.
  - `cleaned/`: Directory for cleaned scraped data.
    - `cleaning.ipynb`: Jupyter notebook for cleaning the scraped data.


3. **Error and Process Logging:**

    The `logs` directory contains log files that record the scraping activities and any errors encountered. Reviewing these logs can help diagnose and fix issues that arise during the scraping process. This was quite helpful during the process.

    - `scraping-error-logs-nexus.txt`: Contains error logs specific to the Nexus scraping process.
    - `scraping-error-logs-we-the-north.txt`: Contains error logs specific to the We The North scraping process.
    - `scraping-logs-nexus.txt`: Contains general logs for the Nexus scraping process.
    - `scraping-logs-we-the-north.txt`: Contains general logs for the We The North scraping process.

4. **Data Cleaning:**

    After scraping, the raw data can be cleaned using the Jupyter notebook provided in `scraped/cleaned/cleaning.ipynb`. This notebook contains steps to process and clean the scraped data for further analysis.

---

### Dashboard