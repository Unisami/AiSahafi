import requests
from config import WP_API_URL, WP_USERNAME, WP_PASSWORD, PEXELS_API_KEY

class Publish:
    def __init__(self, article):
        self.article = article
        self.wp_categories = {
            'AI': 7,           # 'Artificial Intelligence'
            'Tech': 6,         # 'Tech'
            'Business': 8,     # 'Business'
            'Mix': 9          # 'Mix'
        }
        self.supported_image_types = ['jpg', 'jpeg', 'png', 'gif']
    
    def get_category_from_content(self):
        keywords = {
            'AI': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'gpt', 'openai', 'bot', 'automation'],
            'Tech': ['software', 'hardware', 'technology', 'app', 'device', 'smartphone', 'computer', 'platform', 'digital'],
            'Business': ['startup', 'funding', 'investment', 'acquisition', 'revenue', 'market', 'company', 'valuation', 'venture']
        }

        category_scores = {key: 0 for key in keywords.keys()}

        for keyword, phrases in keywords.items():
            for phrase in phrases:
                if phrase in self.article.get('content', ''):
                    category_scores[keyword] += 1

        return (max(category_scores, key=category_scores.get) if max(category_scores.values()) > 0 else 'Mix')

    def upload_media_to_wordpress(self, image_url):
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
                auth=requests.auth.HTTPBasicAuth(WP_USERNAME, WP_PASSWORD),
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
        except Exception as e:
            print(f"❌ Error searching for image on Pexels: {str(e)}")
            return None

    def upload_article(self):
        """Upload article to WordPress with category and featured image"""
        try:
            # Get appropriate category
            category_name = self.get_category_from_content()
            category_id = self.wp_categories.get(category_name)
            
            if not category_id:
                print(f"⚠️ Category not found: {category_name}, using default")
                category_id = self.wp_categories.get('Mix', 1)  # Default to Mix or ID 1
            
            # Get relevant image from Pexels
            image_info = self.get_pexels_image(self.article['title'])

            # Prepare post data
            post_data = {
                'title': self.article['title'],
                'content': self.article['content'],
                'status': 'publish',
                'categories': [category_id],
                'meta': {
                    'source_url': self.article.get('link', ''),
                    'author': self.article.get('author', '')
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
                auth=requests.auth.HTTPBasicAuth(WP_USERNAME, WP_PASSWORD),
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded: {self.article['title']}")
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
