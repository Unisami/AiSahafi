from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# WordPress Configuration
WP_API_URL = os.getenv('WP_API_URL')
WP_USERNAME = os.getenv('WP_USERNAME')
WP_PASSWORD = os.getenv('WP_PASSWORD')

# DeepSeek Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Pexels Configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY') 