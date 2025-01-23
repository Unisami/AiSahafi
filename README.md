# Automated AI News Website

## Overview

The Automated AI News Website is a fully automated platform that scrapes and aggregates news articles focused on Artificial Intelligence (AI) and Business. The website uses AI to rewrite articles in a unique style and optimizes content with SEO keywords before publishing it automatically. This project aims to provide users with timely and relevant news from trusted sources in the AI and business domains.

## Features

- **News Aggregation**: Automatically fetches articles from trusted news sources
- **Content Rewriting**: Utilizes DeepSeek AI to rewrite articles in a personalized style
- **SEO Optimization**: Automatically adds relevant SEO keywords to improve search visibility
- **Automated Publishing**: Uploads articles to WordPress without manual intervention
- **Image Integration**: Automatically fetches relevant images from Pexels
- **Category Management**: Smart categorization of articles into AI, Tech, Business, or Mix
- **Duplicate Prevention**: Uses MD5 hashing to prevent duplicate articles
- **Modern UI**: Responsive design with Tailwind CSS and animated backgrounds

## Technologies Used

### Backend
- Python 3.11+
- Flask (Web Framework)
- SQLAlchemy (Database ORM)
- Beautiful Soup (Web Scraping)
- Feedparser (RSS Feed Parsing)

### Frontend
- HTML5
- Tailwind CSS
- JavaScript (Animations & Loading States)

### APIs & Services
- DeepSeek API (Content Generation)
- Pexels API (Image Integration)
- WordPress REST API (Content Management)
- TechCrunch RSS Feed (News Source)

### Database
- SQLite (Local Development)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Pip (Python package installer)
- WordPress installation with REST API enabled
- API keys for:
  - DeepSeek
  - Pexels
  - WordPress credentials

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

3. **Environment Setup**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   WP_API_URL=your_wordpress_api_url
   WP_USERNAME=your_wordpress_username
   WP_PASSWORD=your_wordpress_password
   DEEPSEEK_API_KEY=your_deepseek_api_key
   PEXELS_API_KEY=your_pexels_api_key
   ```

### Usage

1. **Start the Flask Server**:
   ```bash
   python app.py
   ```
   This will start the web interface on `http://localhost:5000`

2. **Run the Content Pipeline**:
   ```bash
   python main.py
   ```
   This will:
   - Fetch latest articles from TechCrunch
   - Rewrite content using DeepSeek AI
   - Add relevant images from Pexels
   - Publish to WordPress
   - Update the local database

## Project Structure

AiSahafi/
├── app.py              # Flask application
├── main.py            # Content processing pipeline
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
├── hash-logs.txt     # Duplicate prevention logs
├── templates/        # HTML templates
│   ├── index.html    # Homepage template
│   ├── all.html      # All articles page
│   └── article.html  # Single article page
└── static/           # Static assets

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

