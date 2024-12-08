# Automated AI News Website

## Overview

The Automated AI News Website is a fully automated platform that scrapes and aggregates news articles focused on Artificial Intelligence (AI) and Business. The website uses AI to rewrite articles in a unique style and optimizes content with SEO keywords before publishing it automatically. This project aims to provide users with timely and relevant news from trusted sources in the AI and business domains.

## Features

- **News Aggregation**: Automatically fetches articles from trusted news sources.
- **Content Rewriting**: Utilizes AI to rewrite articles in a personalized style.
- **SEO Optimization**: Automatically adds relevant SEO keywords to improve search visibility.
- **Automated Publishing**: Uploads articles to the website without manual intervention.

## Technologies Used

- Python
- Beautiful Soup (for web scraping)
- TechCrunch (for fetching news articles)
- Feedparser (for parsing RSS feeds)
- A custom AI model for content rewriting (e.g., OpenAI GPT)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Pip (Python package installer)
- An API key from OpenAI

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Unisami/AiSahafi
   cd AiSahafi
   ```

2. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   - go to main.py and setup your openai API

### Usage

1. **Start the Flask Server**:
   - You can start the Flask server by running:

   ```bash
   python app.py
   ```

2. **Run the content scraping, rewriting and uploading script by running:**:
   - It will scrape, rewrite and upload all the new articles onto the site:

   ```bash
   python main.py
   ```


### Customization

- You can customize the keywords used for scraping and the AI rewriting styles by modifying.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

