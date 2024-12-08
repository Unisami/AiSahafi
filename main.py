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

class MainApp:
    def __init__(self, rss_url='https://techcrunch.com/feed/'):
        # OpenAI Client Setup
        self.client = AzureOpenAI(
            api_key="OPEN-AI API KEY",
            api_version="2024-02-15-preview",
            azure_endpoint="add azure if you use it"
        )


        # Web Scraping Setup
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.session = self._create_session()
        self.rss_url = rss_url
    
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

    def rewrite_article(self, article: Dict) -> Dict:
        try:
            response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a direct, no-BS tech expert who focuses on practical value and results. "
                                        "Add citations and references to help non-technical readers understand easily.\n\n"
                                        "Writing Style Rules:\n"
                                        "1) Use specific numbers/metrics\n"
                                        "2) Focus on actionable insights\n"
                                        "3) Include citations and expert references\n"
                                        "4) Add a P.S. \n"
                                        "5) Add links to the references if you think its good\n\n"
                                        "Content Guidelines:\n"
                                        "- Use conversational, simple language (7th grade level)\n"
                                        "- Write short, punchy sentences\n"
                                        "- Include analogies and examples\n"
                                        "- Use personal anecdotes where relevant\n"
                                        "- Add bullet points for key information\n"
                                        "- Split long sentences for readability\n"
                                        "- Use bold/italic for emphasis\n"
                                        "- Avoid jargon and promotional language\n\n"
                                        "Tone: Confident but friendly, using phrases like 'Here's the deal:', 'Straight up:', 'Zero fluff'\n\n"
                                        "\n\nGenerate articles using this exact HTML/Tailwind CSS template:"
                                        "\n<article class='max-w-4xl mx-auto px-6 py-8'>"
                                        "\n  <div class='mb-8'>"
                                        "\n    <h2 class='text-3xl font-bold text-purple-300 mb-4'>{{article.title}}</h2>"
                                        "\n    <div class='flex justify-between items-center text-gray-400 border-b border-gray-700 pb-4'>"
                                        "\n      <span class='text-sm'>{{article.date}}</span>"
                                        "\n    </div>"
                                        "\n  </div>"
                                        "\n  <div class='prose prose-invert max-w-none'>"
                                        "\n    <div class='text-gray-300 leading-relaxed space-y-6'>"
                                        "\n      [CONTENT HERE - Use the following components:]"
                                        "\n      <!-- Paragraphs -->"
                                        "\n      <p class='text-gray-300 mb-4'></p>"
                                        "\n      <!-- Subheadings -->"
                                        "\n      <h3 class='text-xl font-semibold text-purple-200 mt-8 mb-4'></h3>"
                                        "\n      <!-- Lists -->"
                                        "\n      <ul class='list-disc ml-6 space-y-2 text-gray-300'>"
                                        "\n        <li></li>"
                                        "\n      </ul>"
                                        "\n      <!-- Quotes -->"
                                        "\n      <blockquote class='border-l-4 border-purple-400 pl-4 my-6 italic text-gray-400'></blockquote>"
                                        "\n      <!-- Important text -->"
                                        "\n      <span class='text-purple-300 font-medium'></span>"
                                        "\n    </div>"
                                        "\n  </div>"
                                        "\n</article>"
                                        + "\n\n[Rest of your existing writing style guidelines...]"
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        f"Rewrite this tech article in your style: \n\n{article['content']}"
                                    ),
                                }
                            ],
                    temperature=0.7,
                    top_p=1,
                    frequency_penalty=0.2,
                    presence_penalty=0.1,
                )    
            
            rewritten_content = response.choices[0].message.content.strip()
            # Remove 'html' prefix if present
            rewritten_content = re.sub(r'^(?:html|```html|```)\s*', '', rewritten_content, flags=re.IGNORECASE)

            return {
                'title': article['title'],
                'author': article.get('author'),
                'date': article.get('date'),
                'content': rewritten_content,
                'preview': self.strip_html(rewritten_content)  # Add preview field
            }
            
        except Exception as e:
            print(f"Error rewriting article: {str(e)}")
            return article  # Return original article if rewriting fails
    
    def strip_html(self, html_content: str) -> str:
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        # Limit preview length to first 200 characters
        return clean_text[:200] + '...' if len(clean_text) > 200 else clean_text
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
            article_hash = self.hash_md5(article)

            if self.does_hash_exist(article_hash, existing_hashes):
                print(f"Skipping duplicate article: {article['title']}")
                continue

            
            print(f"Processing article: {article['title']}")

            content = self.scrape_news_from_link(article['link']) 
            if content:
                article['content'] = content
                rewritten_article = self.rewrite_article(article) 

                if self.upload_article(rewritten_article): 
                    processed_articles.append(rewritten_article)
                    self.save_hash(article_hash)
                    existing_hashes.add(article_hash)  # Update in-memory set

        print(f"\nProcessed {len(processed_articles)} articles.")
        return processed_articles

    def upload_article(self, article, upload_url="http://localhost:5000/upload"):
        article_data = {
            'title': article['title'],
            'content': article['content']['content'].replace('```', '') if isinstance(article['content'], dict) else article['content'].replace('```', ''),
            'author': article.get('author', 'No author'),
            'preview': article.get('preview'),  # Add preview field
            'date': article.get('date') or article.get('published_date', 'No date'),
            'link': article.get('link', '')
        }

        try:
            response = requests.post(upload_url, json=article_data)
            if response.status_code == 200:
                print(f"Successfully uploaded article: {article['title']}")
                return True
            else:
                print(f"Failed to upload article: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error uploading article: {str(e)}")
            return False


def main():
    processor = MainApp()
    processor.process_articles()

if __name__ == "__main__":
    main()