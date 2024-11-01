# TruthSocial Dataset - The 2024 Election Integrity Initiative 

TruthSocial, launched as a social media platform with a focus on free speech, has become a prominent space for political discourse, attracting a user base with diverse, often conservative, viewpoints. As an emerging platform with minimal content moderation, Truth Social has facilitated discussions around contentious social and political issues but has also seen the spread of conspiratorial and hyper-partisan narratives.

This release is a comprehensive dataset capturing activity on TruthSocial related to the upcoming 2024 US Presidential Election, including posts, comments, user profiles, and interactions. This dataset comprises 1.5 million posts published between February 2022 and October 2024 and encompasses key metadata and user engagement metrics.

### Key Features of the Dataset

- **Timeframe**: February 2022 - October 2024
- **Number of Posts**: 1.5 million
- **Included Data**: Posts, comments, user profiles, and interactions
- **Metrics**: Key metadata and user engagement metrics

Please find the dataset [here](https://www.kaggle.com/datasets/kashishashah/truthsocial-2024-election-integrity-initiative)

### Purpose and Research Potential

This dataset offers researchers a unique resource to study:
- **Communication Patterns**: Analysis of how users communicate and engage on the platform.
- **Community Formation**: Insights into how online communities form and interact within Truth Social.
- **Dissemination of Information**: Understanding how information, including political and social narratives, spreads on the platform.

### Goals

By providing an in-depth view of TruthSocial’s user dynamics and content distribution, this dataset aims to:
- Support further research on political discourse within an alt-tech social media platform.
- Enable analysis of the impact of limited content moderation on political discussions and information dissemination.

## Directory Structure - Scripts

The repository includes a `scripts` folder containing tools to scrape, process, and analyze the dataset. Each script’s purpose is outlined below:

- **`auto_fire_scraper.py`**: A script to automate the scraping process for trending keywords, capturing related posts and metadata over a specified time frame.
- **`auto_fire_scraper_persistent_keywords.py`**: Similar to `auto_fire_scraper.py`, but it continuously scrapes using a persistent set of keywords to ensure ongoing data collection.
- **`data_pipeline.py`**: The main data pipeline script for cleaning, processing, and structuring the raw data, ensuring consistent formatting and removing duplicates.
- **`keyword_mappings.json`**: A JSON file containing mappings for various keywords and tags, normalizing them for consistent analysis.
- **`scrape_one_keyword.py`**: A targeted scraper that collects data for a single keyword, allowing focused data collection on trending topics.
- **`scrape_one_keyword_persistent_keywords.py`**: Similar to `scrape_one_keyword.py`, but with persistent scraping enabled for continuous data collection on a single keyword.


This [initiative](https://election-integrity.online/) is led by Prof. Emilio Ferrara who leads the USC Humans Lab at USC Information Sciences Institute. 

