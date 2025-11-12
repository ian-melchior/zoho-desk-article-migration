"""
Proof of concept: Test Zoho OAuth authentication and make a simple API call.
This verifies our credentials work before building the full migration system.
"""

import os
import requests
from datetime import datetime

def test_authentication():
  # can we get an access toekn from our refresh token?
  print("=" * 60)
  print("TEST 1: Authentication)
  print("=" * 60)

  # Get credentials from environment variables
  client_id = os.environ.get('ZOHO_CLIENT_ID')
  client_secret = os.environ.get('ZOHO_CLIENT_SECRET')
  refresh_token = os.environ.get('ZOHO_REFRESH_TOKEN')

  # Check if we have all credentials
  if not all([client_id, client_secret, refresh_token]):
      print("✗ Missing credentials in environment variables!")
      return None

  print(f"✓ Found all credentials")
      print(f"  Client ID: {client_id[:10]}...")
      print(f"  Refresh Token: {refresh_token[:10]}...")
  # Try to get an access token
  token_url = "https://accounts.zoho.com/oauth/v2/token"
  params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
  print("\nAttempting to refresh access token...")
  try:
          response = requests.post(token_url, params=params)
          
          # Check if request was successful
          if response.status_code == 200:
              tokens = response.json()
              
              if 'access_token' in tokens:
                  access_token = tokens['access_token']
                  print(f"✓ SUCCESS! Got access token: {access_token[:20]}...")
                  return access_token
              else:
                  print(f"✗ FAILED: Response missing access_token")
                  print(f"  Response: {tokens}")
                  return None
          else:
              print(f"✗ FAILED: HTTP {response.status_code}")
              print(f"  Response: {response.text}")
              return None
              
      except Exception as e:
          print(f"✗ ERROR: {e}")
          return None

def test_api_call(access_token):
    """
    Test 2: Can we make a simple API call to Zoho Desk?
    """
    print("\n" + "=" * 60)
    print("TEST 2: API Call")
    print("=" * 60)
    
    org_id = os.environ.get('ZOHO_ORG_ID')
    
    if not org_id:
        print("X Missing ZOHO_ORG_ID in environment variables!")
        return False
    
    print(f"+ Using Org ID: {org_id}")
    
    # Try to fetch articles
    url = "https://desk.zoho.com/api/v1/articles"
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "orgId": org_id
    }
    
    print(f"\nCalling API: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            article_count = len(data.get('data', []))
            
            print(f"+ SUCCESS! API call worked!")
            print(f"  Found {article_count} articles")
            
            # Show first 3 article titles
            if article_count > 0:
                print("\n  Sample articles:")
                for i, article in enumerate(data['data'][:3], 1):
                    title = article.get('title', 'Untitled')
                    article_id = article.get('id', 'No ID')
                    print(f"    {i}. [{article_id}] {title}")
            
            return True
        else:
            print(f"X FAILED: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"X ERROR: {e}")
        return False


def main():
    """
    Run all tests in sequence.
    """
    print("\nZOHO DESK API PROOF OF CONCEPT")
    print(f"Started at {datetime.now()}\n")
    
    # Test 1: Authentication
    access_token = test_authentication()
    
    if not access_token:
        print("\nAuthentication failed. Cannot proceed to API test.")
        print("\nTroubleshooting:")
        print("  1. Check that your secrets are correctly set in GitHub")
        print("  2. Verify your refresh token hasn't expired")
        print("  3. Make sure client ID and secret match your Zoho API Console")
        return
    
    # Test 2: API Call
    api_success = test_api_call(access_token)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Authentication: {'+ PASS' if access_token else 'X FAIL'}")
    print(f"API Call:       {'+ PASS' if api_success else 'X FAIL'}")
    
    if access_token and api_success:
        print("\nAll tests passed! You're ready to build the migration.")
    else:
        print("\nSome tests failed. Fix issues before proceeding.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
