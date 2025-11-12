"""
Zoho Desk API client module.
Provides methods for interacting with Zoho Desk endpoints.
"""
import requests


class ZohoDeskAPI:
    """
    Client for Zoho Desk API operations.
    
    This class wraps the Zoho Desk REST API and provides methods for:
    - Fetching articles (single or multiple)
    - Creating articles
    - Updating articles
    
    Each method handles authentication, request formatting, and error handling.
    
    Usage:
        from src.zoho_auth import ZohoAuth
        
        auth = ZohoAuth(client_id, client_secret, refresh_token)
        api = ZohoDeskAPI(auth, org_id)
        
        article = api.get_article_by_id("123456789")
    """
    
    def __init__(self, auth, org_id):
        """
        Initialize the API client.
        
        Args:
            auth (ZohoAuth): An authenticated ZohoAuth instance
            org_id (str): Your Zoho Desk organization ID
        """
        # Store the auth handler so we can get access tokens
        self.auth = auth
        
        # Organization ID - required for all Zoho Desk API calls
        self.org_id = org_id
        
        # Base URL for all Zoho Desk API endpoints
        self.base_url = "https://desk.zoho.com/api/v1"
    
    def _get_headers(self, include_content_type=False):
        """
        Private helper method to build request headers.
        
        Methods starting with underscore are "private" by convention -
        they're meant to be used internally by the class, not called directly.
        
        This ensures we always have a valid access token and proper headers
        for every API request.
        
        Args:
            include_content_type (bool): Whether to add Content-Type header
                                         (needed for POST/PATCH with JSON body)
        
        Returns:
            dict: Headers dictionary ready for requests
        """
        # Make sure we have a valid access token
        if not self.auth.access_token:
            self.auth.get_access_token()
        
        # Build the headers dictionary
        headers = {
            # Zoho requires this specific format for OAuth tokens
            "Authorization": f"Zoho-oauthtoken {self.auth.access_token}",
            
            # orgId tells Zoho which organization's data to access
            "orgId": self.org_id
        }
        
        # For POST/PATCH requests, we need to specify we're sending JSON
        if include_content_type:
            headers["Content-Type"] = "application/json"
        
        return headers
    
    def get_article_by_id(self, article_id):
        """
        Fetch a single article by its ID.
        
        This is the method we'll use first to inspect what data we get back
        from Zoho Desk for a single article.
        
        Args:
            article_id (str): The Zoho Desk article ID
        
        Returns:
            dict: Article data if successful, None if error
                  Article dict contains fields like:
                  - id: Article ID
                  - title: Article title
                  - answer: Article content (HTML)
                  - categoryId: Category ID
                  - departmentId: Department ID
                  - status: PUBLISHED, DRAFT, etc.
                  - and many more...
        """
        # Get headers with valid auth token
        headers = self._get_headers()
        
        # Build the full URL for this specific article
        url = f"{self.base_url}/articles/{article_id}"
        
        print(f"[API] Fetching article {article_id} from {url}")
        
        try:
            # Make GET request to fetch the article
            response = requests.get(url, headers=headers)
            
            # Raise exception for bad status codes (404, 500, etc.)
            response.raise_for_status()
            
            # Parse the JSON response
            article_data = response.json()
            
            print(f"[API] Successfully fetched article: {article_data.get('title', 'Untitled')}")
            
            return article_data
            
        except requests.exceptions.HTTPError as e:
            # HTTP error (404 Not Found, 403 Forbidden, etc.)
            print(f"[API] HTTP error fetching article {article_id}: {e}")
            print(f"[API] Response: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            # Network error or other request problem
            print(f"[API] Network error fetching article {article_id}: {e}")
            return None
    
    def get_articles(self, limit=None, from_index=None):
        """
        Fetch multiple articles from Zoho Desk.
        
        This endpoint returns a paginated list of articles.
        We'll use this later for batch operations.
        
        Args:
            limit (int, optional): Maximum number of articles to fetch (max 100)
            from_index (int, optional): Starting index for pagination
        
        Returns:
            dict: API response containing:
                  - data: List of article objects
                  - count: Number of articles returned
                  Returns None if error
        """
        headers = self._get_headers()
        url = f"{self.base_url}/articles"
        
        # Build query parameters for pagination
        params = {}
        if limit:
            params['limit'] = limit
        if from_index:
            params['from'] = from_index
        
        print(f"[API] Fetching articles (limit={limit}, from={from_index})")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            article_count = len(data.get('data', []))
            
            print(f"[API] Successfully fetched {article_count} articles")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"[API] Error fetching articles: {e}")
            return None
    
    def create_article(self, article_data):
        """
        Create a new article in Zoho Desk.
        
        This will be used in step 2 when we test posting an article.
        
        Args:
            article_data (dict): Article fields to create
                Required fields typically include:
                - title: Article title
                - answer: Article content (can be HTML)
                - categoryId: Category ID where article belongs
                
                Optional fields might include:
                - departmentId: Department ID
                - tags: List of tag strings
                - status: PUBLISHED or DRAFT
                - authorId: Author user ID
                
                See Zoho Desk API docs for complete field list
        
        Returns:
            dict: Created article data if successful, None if error
        """
        # Get headers including Content-Type for JSON body
        headers = self._get_headers(include_content_type=True)
        
        url = f"{self.base_url}/articles"
        
        print(f"[API] Creating article: {article_data.get('title', 'Untitled')}")
        
        try:
            # Make POST request with article data as JSON
            response = requests.post(url, headers=headers, json=article_data)
            response.raise_for_status()
            
            result = response.json()
            
            print(f"[API] Successfully created article with ID: {result.get('id')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"[API] Error creating article: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[API] Response: {e.response.text}")
            return None
    
    def update_article(self, article_id, article_data):
        """
        Update an existing article in Zoho Desk.
        
        We might need this for advanced migration scenarios.
        
        Args:
            article_id (str): The article ID to update
            article_data (dict): Fields to update (only include fields you want to change)
        
        Returns:
            dict: Updated article data if successful, None if error
        """
        headers = self._get_headers(include_content_type=True)
        
        url = f"{self.base_url}/articles/{article_id}"
        
        print(f"[API] Updating article {article_id}")
        
        try:
            # PATCH only updates the fields you provide, doesn't replace entire article
            response = requests.patch(url, headers=headers, json=article_data)
            response.raise_for_status()
            
            result = response.json()
            
            print(f"[API] Successfully updated article {article_id}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"[API] Error updating article {article_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[API] Response: {e.response.text}")
            return None
