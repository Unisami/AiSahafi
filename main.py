from agents import Agents
from publish import Publish
from scraper import Scraper
import re
def main():
    # Initialize classes
    agents = Agents()
    scraper = Scraper()

    # Start the news scraping and publishing process
    articles = scraper.scrape_news()

    for article in articles:
        # Summarize the article
        summarized_content = agents.summariser(article)
        print(f"Summarized Content: {summarized_content[:50]}...")

        # Optimize for SEO
        seo_content = agents.seo_optimiser(summarized_content)
        print(f"SEO Optimized Content: {seo_content[:50]}...")
        seo_content = re.sub(r'^(?:html|```html|```)\s*', '', seo_content, flags=re.IGNORECASE)
        article['content'] = seo_content
        # Prepare to publish
        publisher = Publish(article)
        publisher.upload_article()


if __name__ == "__main__":
    main()