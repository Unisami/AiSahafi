from google import genai
from config import GEMINI_API_KEY, summariser_prompt, seo_optimiser_prompt

class Agents:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)


    def summariser(self, article):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""{summariser_prompt} Rewrite this tech article in your style.
            Title: {article['title']}
            Date: {article.get('date', 'Not specified')}
            Content: {article['content']}
            Please maintain the article's factual accuracy while making it more engaging."""
        )
        return response.text
    

    def seo_optimiser(self, article_content):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{seo_optimiser_prompt} Optimize this tech article for SEO: {article_content}"
        )
        return response.text

