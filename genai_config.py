# GenAI Configuration for Invoice Approval System

# OpenAI API Configuration
OPENAI_API_KEY = "sk-proj-SAMPLE-KEY-FOR-TESTING-12345"  # Replace with actual key
OPENAI_MODEL = "gpt-4"  # Options: "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"

# Enable/Disable GenAI
USE_GENAI = True  # Set to False to use rule-based evaluation only

# API Endpoint (for custom deployments)
OPENAI_API_BASE = "https://api.openai.com/v1"

# Model Parameters
TEMPERATURE = 0.3  # Lower = more deterministic, Higher = more creative
MAX_TOKENS = 500

# Fallback to rule-based if GenAI fails
FALLBACK_TO_RULES = True

# How to get an API key:
# 1. Visit https://platform.openai.com/account/api-keys
# 2. Create a new API key
# 3. Replace OPENAI_API_KEY with your actual key
# 4. Keep it secret - don't commit to version control

# Sample API key format (not valid):
# sk-proj-XXXXXXXXXXXXXXXXXXXXXXXX...
