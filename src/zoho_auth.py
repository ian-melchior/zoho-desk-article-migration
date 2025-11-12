"""
Zoho OAuth2 authentication module.
Handles token refresh and management for Zoho API access.
"""
import requests
from datetime import datetime


class ZohoAuth:
    """
    Manages OAuth2 authentication with Zoho services.
    
    This class handles:
    - Storing OAuth credentials (client ID, secret, refresh token)
    - Refreshing access tokens when needed
    - Providing valid access tokens for API calls
    
    Usage:
        auth = ZohoAuth(client_id, client_secret, refresh_token)
        access_token = auth.get_access_token()
    """
    
    def __init__(self, client_id, client_secret, refresh_token):
        """
        Initialize the authentication handler.
        
        Args:
            client_id (str): Your Zoho API client ID
            client_secret (str): Your Zoho API client secret
            refresh_token (str): Your permanent refresh token from Zoho
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        
        # This will hold the current access token (expires in ~1 hour)
        self.access_token = None
        
        # Zoho's OAuth token endpoint
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    def get_access_token(self):
        """
        Get a valid access token, refreshing if necessary.
        
        OAuth2 refresh flow:
        1. Send refresh_token + credentials to Zoho
        2. Receive new access_token (valid for ~1 hour)
        3. Store and return the access_token
        
        Returns:
            str: Valid access token, or None if refresh failed
        """
        # Build the request parameters per Zoho's OAuth2 spec
        params = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            # Make POST request to Zoho's token endpoint
            response = requests.post(self.token_url, params=params)
            
            # Raise exception if we got an error status code
            response.raise_for_status()
            
            # Parse JSON response
            tokens = response.json()
            
            # Check if we got an access token back
            if 'access_token' in tokens:
                self.access_token = tokens['access_token']
                print(f"[Auth] Access token refreshed at {datetime.now()}")
                return self.access_token
            else:
                # Response didn't contain access_token - something's wrong
                print(f"[Auth] Error: Response missing access_token")
                print(f"[Auth] Response: {tokens}")
                return None
                
        except requests.exceptions.RequestException as e:
            # Network error or bad response
            print(f"[Auth] Network error refreshing token: {e}")
            return None
    
    def is_token_valid(self):
        """
        Check if we have a current access token.
        
        Note: This doesn't verify the token is still valid with Zoho,
        just that we have one stored. Access tokens expire after ~1 hour.
        
        Returns:
            bool: True if we have a token stored, False otherwise
        """
        return self.access_token is not None