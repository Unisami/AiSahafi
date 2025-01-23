import requests
from openai import AzureOpenAI
from typing import Dict, List
import feedparser
from bs4 import BeautifulSoup
import random
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import hashlib
import re
import base64
import json
from wordpress_config import WP_API_URL, WP_USERNAME, WP_PASSWORD
from requests.auth import HTTPBasicAuth
from config import PEXELS_API_KEY
from deepseek_config import DEEPSEEK_API_KEY
class MainApp:
    def __init__(self, rss_url='https://techcrunch.com/feed/'):
        # Setup DeepSeek client
        self.client = requests.Session()
        self.client.headers.update({
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',  # Correct Bearer token format
            'Content-Type': 'application/json'
        })
        self.deepseek_api_url = "https://api.deepseek.com/chat/completions"  # Correct endpoint
        
        # Web Scraping Setup
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.session = self._create_session()
        self.rss_url = rss_url
        # Initialize categories
        self.wp_categories = {
            'AI': 7,           # 'Artificial Intelligence'
            'Tech': 6,         # 'Tech'
            'Business': 8,     # 'Business'
            'Mix': 9          # 'Mix'
        }
        
        # Add supported image types
        self.supported_image_types = ['jpg', 'jpeg', 'png', 'gif']

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,

            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def parse_rss_feed(self) -> List[Dict]:
        print("\nParsing RSS feed...")
        feed = feedparser.parse(self.rss_url)
        print(f"Found {len(feed.entries)} entries in feed")
        articles = []
        
        for entry in feed.entries:
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

    def scrape_news_from_link(self, link) -> Dict:
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(
                link, 
                headers={'User-Agent': random.choice(self.user_agents)}, 
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
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

    def strip_html(self, html_content: str) -> str:
        import re
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        # Limit preview length to first 200 characters
        return clean_text[:200] + '...' if len(clean_text) > 200 else clean_text

    def rewrite_article(self, article: Dict) -> Dict:
        try:
            # Prepare the message for DeepSeek
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Content Creation Expert Configuration:\n\n"
                            
                            "Identity:\n"
                            "You are a high-energy, FOMO-inducing content expert who transforms boring topics into POWERFUL, engaging content. "
                            "Your mission is creating content that HITS DIFFERENT, credible and engaging content that genuinely connects with readers.\n\n"

                            "Core Writing Principles:\n"
                            "1) Back claims with concrete data and examples\n"
                            "2) Deliver practical, implementable insights\n"
                            "3) Support with expert opinions and research\n" 
                            "4) Conclude memorably and meaningfully\n"
                            "5) Reference authoritative sources\n\n"
                            
                            "Article HTML Structure and DO NOT USE ANY OTHER FORMAT, ONLY HTML ELEMENTS AND SLIGHT CSS FOR EACH THING, Just make it beautiful, and use other html tags not mentioned to make it structured:\n"
                            "<article>\n"
                            "    <header>\n"
                            "        <h1>{{article.title}}</h1>\n"
                            "        <div class='meta'>\n"
                            "            <time datetime='{{article.date}}'>{{article.date}}</time>\n"
                            "        </div>\n"
                            "    </header>\n"
                            "    \n"
                            "    <div class='content'>\n"
                            "        <h2></h2>\n"
                            "        <p>/p>\n"
                            "        <ul>\n"
                            "            <li></li>\n"
                            "        </ul>\n"
                            "        <blockquote>\n"
                            "            <p>/p>\n"
                            "            <cite>{</cite>\n"
                            "        </blockquote>\n"
                            "    </div>\n"
                            "</article>\n\n"
                            
                            "Content Development Guidelines:\n\n"

                            "Reader Impact Strategy\n\n"
                            "- Hit them with ENERGY they can't ignore\n"
                            "- Share WAR STORIES that prove your worth\n"
                            "- Use metaphors that WAKE THEM UP\n"
                            "- Make readers feel the POWER in every word\n\n"

                            "Content Domination Framework\n\n"
                            "- Hook that GRABS them by the throat\n"
                            "- Sections that BUILD like a crescendo\n"
                            "- Headlines that DEMAND attention\n"
                            "- Bullets that PUNCH through resistance\n"
                            "- Short, SHARP paragraphs that command attention\n"
                            "- Conclusions that FORCE action\n\n"

                            "Language of WINNERS\n\n"
                            "- Write like you're in the TRENCHES with them\n"
                            "- CRYSTAL CLEAR communication\n"
                            "- ACTIVE voice that COMMANDS\n"
                            "- Stories that PROVE your worth\n"
                            "- Balance between BEAST MODE and WISDOM\n"
                            "- Cut the weak jargon\n"
                            "- Break down complexity like a BOSS\n\n"

                            "Engagement MAXIMIZATION\n\n"
                            "- Examples that PROVE IT WORKS\n"
                            "- Questions that MAKE THEM THINK\n"
                            "- Transitions smooth as SILK\n"
                            "- Expert quotes that CRUSH DOUBT\n"
                            "- Key points that STICK LIKE GLUE\n"
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Rewrite this tech article in your style.\n\n"
                            f"Title: {article['title']}\n"
                            f"Date: {article.get('date', 'Not specified')}\n"
                            f"Content:\n{article['content']}\n\n"
                            "Please maintain the article's factual accuracy while making it more engaging."
                        )
                    }
                ],
                "stream": False,
                "temperature": 0.7
            }

            # Make request to DeepSeek API
            response = self.client.post(
                self.deepseek_api_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            rewritten_content = result['choices'][0]['message']['content'].strip()
            
            # Remove any HTML prefix if present
            rewritten_content = re.sub(r'^(?:html|```html|```)\s*', '', rewritten_content, flags=re.IGNORECASE)

            return {
                'title': article['title'],
                'author': article.get('author'),
                'date': article.get('date'),
                'content': rewritten_content,
                'preview': self.strip_html(rewritten_content)
            }
            
        except Exception as e:
            print(f"Error rewriting article: {str(e)}")
            print(f"Response status code: {getattr(response, 'status_code', 'N/A')}")
            print(f"Response text: {getattr(response, 'text', 'N/A')}")
            return article  # Return original article if rewriting fails

    def get_category_from_content(self, title, content):
        """Determine article category based on keywords"""
        # Keywords for each category
        keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'gpt', 'openai', 'bot', 'automation'],
            'Tech': ['software', 'hardware', 'technology', 'app', 'device', 'smartphone', 'computer', 'platform', 'digital'],
            'Business': ['startup', 'funding', 'investment', 'acquisition', 'revenue', 'market', 'company', 'valuation', 'venture']
        }
        
        text = (title + ' ' + content).lower()
        
        # Count keyword matches for each category
        scores = {category: 0 for category in keywords}
        for category, category_keywords in keywords.items():
            for keyword in category_keywords:
                if keyword in text:
                    scores[category] += 1
        
        # Debug info
        print("\nCategory Detection:")
        for category, score in scores.items():
            print(f"{category}: {score} matches")
        
        # Get category with highest score
        max_score = max(scores.values())
        if max_score > 0:
            category = max(scores, key=scores.get)
            print(f"Selected category: {category} (score: {max_score})")
            return category
        
        # Default to Mix if no strong category match
        print("No strong category match, defaulting to Mix")
        return 'Mix'

    def get_pexels_image(self, query):
        """Search and download relevant image from Pexels"""
        try:
            headers = {
                'Authorization': PEXELS_API_KEY
            }
            
            # Search for images
            search_url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data['photos']:
                    photo = data['photos'][0]
                    # Use medium size and clean the URL
                    image_url = photo['src']['medium'].split('?')[0]  # Remove URL parameters
                    
                    # Get base filename without parameters
                    filename = image_url.split('/')[-1]
                    image_ext = filename.split('.')[-1].lower()
                    
                    if image_ext not in self.supported_image_types:
                        print(f"❌ Unsupported image type: {image_ext}")
                        # Try original format if medium fails
                        image_url = photo['src']['original'].split('?')[0]
                        filename = image_url.split('/')[-1]
                        image_ext = filename.split('.')[-1].lower()
                        
                        if image_ext not in self.supported_image_types:
                            print("❌ Could not find suitable image format")
                            return None
                    
                    # Download and upload image
                    image_id = self.upload_media_to_wordpress(image_url)
                    if image_id:
                        return {
                            'id': image_id,
                            'url': image_url,
                            'photographer': photo['photographer'],
                            'photographer_url': photo['photographer_url']
                        }
            
            print("❌ No suitable image found on Pexels")
            return None
            
        except Exception as e:
            print(f"❌ Error getting Pexels image: {str(e)}")
            return None

    def upload_article(self, article):
        """Upload article to WordPress with category and featured image"""
        try:
            # Get appropriate category
            category_name = self.get_category_from_content(article['title'], article['content'])
            category_id = self.wp_categories.get(category_name)
            
            if not category_id:
                print(f"⚠️ Category not found: {category_name}, using default")
                category_id = self.wp_categories.get('Mix', 1)  # Default to Mix or ID 1
            
            # Get relevant image from Pexels
            image_info = self.get_pexels_image(article['title'])
            
            # Prepare post data
            post_data = {
                'title': article['title'],
                'content': article['content'],
                'status': 'publish',
                'categories': [category_id],
                'meta': {
                    'source_url': article.get('link', ''),
                    'author': article.get('author', '')
                }
            }
            
            # Debug info
            print(f"Debug - Category mapping:")
            print(f"Selected category: {category_name}")
            print(f"Category ID: {category_id}")
            print(f"All categories: {self.wp_categories}")
            
            # Add featured image if available
            if image_info:
                post_data['featured_media'] = image_info['id']
                # Add image credit to content
                credit_html = f'\n\n<p class="image-credit">Image Credit: <a href="{image_info["photographer_url"]}" target="_blank">{image_info["photographer"]}</a> on Pexels</p>'
                post_data['content'] += credit_html
            
            # Upload to WordPress
            response = requests.post(
                f"{WP_API_URL}/posts",
                auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD),
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded: {article['title']}")
                post_url = response.json().get('link')
                print(f"📎 Post URL: {post_url}")
                print(f"📂 Category: {category_name} (ID: {category_id})")
                if image_info:
                    print(f"🖼️ Added featured image from: {image_info['photographer']}")
                return True
            else:
                print(f"❌ Failed to upload article")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading article: {str(e)}")
            return False

    def upload_media_to_wordpress(self, image_url):
        """Upload media to WordPress"""
        try:
            # Download image
            image_response = requests.get(image_url)
            image_data = image_response.content
            
            # Get filename and extension
            filename = image_url.split('/')[-1]
            ext = filename.split('.')[-1].lower()
            
            # Ensure proper content type
            content_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif'
            }
            
            content_type = content_types.get(ext, 'image/jpeg')
            
            # Upload to WordPress
            response = requests.post(
                f"{WP_API_URL}/media",
                auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD),
                files={
                    'file': (filename, image_data, content_type)
                }
            )
            
            if response.status_code in [200, 201]:
                return response.json().get('id')
            else:
                print(f"❌ Failed to upload media")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading media: {str(e)}")
            return None

    def hash_md5(self, data):
        unique_data = f"{data['title']}-{data['link']}"
        return hashlib.md5(unique_data.encode()).hexdigest()

    def load_hashes(self):
        try:
            with open("hash-logs.txt", 'r') as f:
                return set(f.read().splitlines())
        except FileNotFoundError:
            return set()

    def save_hash(self,hash_str):
        with open("hash-logs.txt", 'a') as f:
            f.write(str(hash_str) + '\n')

    def does_hash_exist(self, hash_str, existing_hashes):
        return hash_str in existing_hashes

    def process_articles(self, filter_keywords=None):

        existing_hashes = self.load_hashes()
        processed_articles = []

        articles = self.parse_rss_feed()

        for article in articles:
            try:
                # Add progress tracking
                print(f"\nProcessing {article['title']}")
                
                # Check for duplicates
                article_hash = self.hash_md5(article)
                if self.does_hash_exist(article_hash, existing_hashes):
                    print("⏭️ Skipping duplicate article")
                    continue

                # Get full content
                content = self.scrape_news_from_link(article['link'])
                if not content:
                    print("❌ Failed to get content")
                    continue

                # Rewrite article
                print("🤖 Rewriting article...")
                rewritten = self.rewrite_article(content)
                
                # Upload to WordPress
                print("📤 Uploading to WordPress...")
                if self.upload_article(rewritten):
                    processed_articles.append(rewritten)
                    self.save_hash(article_hash)
                    print("✅ Article processed successfully")
                else:
                    print("❌ Failed to upload article")

            except Exception as e:
                print(f"❌ Error processing article: {str(e)}")
                continue

        print(f"\n✨ Processed {len(processed_articles)} articles")
        return processed_articles

    def setup_categories(self):
        """Setup WordPress categories and get their IDs"""
        try:
            # Get existing categories
            response = requests.get(
                f"{WP_API_URL}/categories",
                auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD)
            )
            
            if response.status_code == 200:
                existing_categories = {cat['name']: cat['id'] for cat in response.json()}
                
                # Create missing categories
                for category in ['AI', 'Tech', 'Business', 'Mix']:
                    if category not in existing_categories:
                        print(f"Creating category: {category}")
                        create_response = requests.post(
                            f"{WP_API_URL}/categories",
                            auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD),
                            json={
                                'name': category,
                                'slug': category.lower()
                            }
                        )
                        
                        if create_response.status_code in [200, 201]:
                            existing_categories[category] = create_response.json()['id']
                        else:
                            print(f"Failed to create category {category}")
                
                # Update category mapping
                self.wp_categories = existing_categories
                print("Categories setup complete:", self.wp_categories)
                
            else:
                print("Failed to get categories")
                
        except Exception as e:
            print(f"Error setting up categories: {str(e)}")




def main():
    processor = MainApp()
    processor.process_articles()

if __name__ == "__main__":
    main()