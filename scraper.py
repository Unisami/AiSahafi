from data import HashStore
import requests, feedparser, time, bs4, random


class Scraper:
    def __init__(self):
        self.rss_url = "https://techcrunch.com/feed/"
        self.session = self._create_session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.',
        ]
        self.hash_store = HashStore()
    def _create_session(self):
        session = requests.Session()
        retry_strategy = requests.adapters.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def parse_rss_feed(self):
        print("\nParsing RSS feed...")
        feed = feedparser.parse(self.rss_url)
        print(f"Found {len(feed.entries)} entries in feed")
        articles = []

        for entry in feed.entries[0:1]:
            article = {
                'title': entry.title,
                'link': entry.link,
                'published_date': entry.get('published', ''),
                'description': entry.get('description', ''),
                'author': entry.get('author', '')
            }
            articles.append(article)
            print(f"Parsed article: {article['title']}")
        return articles
    
    def scrape_news_from_link(self, link):
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(
                link, 
                headers={'User-Agent': random.choice(self.user_agents)}, 
                timeout=15
            )
            response.raise_for_status()
            
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            print(f"\nScraping: {link}")
            
            # Get title
            title = soup.select_one('h1.wp-block-post-title')
            title = title.text.strip() if title else None
            
            # Get author
            author = soup.select_one('div.wp-block-tc23-author-card-name > a')
            author = author.text.strip() if author else None
            
            # Get date
            date = soup.select_one('div.wp-block-post-date > time')
            date = date['datetime'] if date else None
            
            # Get content
            article_content = soup.select_one('div.wp-block-post-content')
            if article_content:
                # Remove ads and unwanted elements
                for unwanted in article_content.select('.ad-unit, .wp-block-tc-ads-ad-slot, .marfeel-experience-inline-cta'):
                    unwanted.decompose()
                
                # Get paragraphs with wp-block-paragraph class
                paragraphs = article_content.select('p.wp-block-paragraph')
                
                if paragraphs:
                    # Filter out short paragraphs and clean text
                    valid_paragraphs = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 50 and not text.startswith('Image Credits:'):
                            valid_paragraphs.append(text)
                    
                    if valid_paragraphs:
                        content = ' '.join(valid_paragraphs)
                        print(f"Found article content: {len(content)} chars")
                        print(f"Preview: {content[:150]}...")
                        
                        return {
                            'title': title,
                            'author': author,
                            'date': date,
                            'content': content
                        }
                        
            print("No valid content found")
            return None
            
        except Exception as e:
            print(f"Error scraping {link}: {str(e)}")
            return None

    def scrape_news(self):
        print("Starting news scraping...")
        articles = self.parse_rss_feed()
        full_articles = []
        for article in articles:
            # Check if the article content already exists
            if self.hash_store.hash_exists(article):
                print(f"Article already exists: {article['title']}")
                continue
            self.hash_store.save_hash(article)

            try:
                full_article = self.scrape_news_from_link(article['link'])
                print(full_article)
                if full_article:
                    full_articles.append(full_article)
            except:
                pass
        return full_articles
