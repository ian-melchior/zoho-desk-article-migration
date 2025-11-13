"""
List ALL categories in both departments, including empty ones.
Uses the Zoho Desk categories API endpoint.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

from src.zoho_auth import ZohoAuth


ACE_DEPT_ID = '986740000000006907'
SJRRC_DEPT_ID = '986740000000403042'


def get_all_categories_raw(auth, org_id):
    """
    Fetch all categories using the API.
    """
    if not auth.access_token:
        auth.get_access_token()
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {auth.access_token}",
        "orgId": org_id
    }
    
    # Try the categories endpoint
    url = "https://desk.zoho.com/api/v1/categories"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None


def main():
    print("=" * 70)
    print("COMPLETE CATEGORY LISTING")
    print(f"Started at {datetime.now()}")
    print("=" * 70)
    
    auth = ZohoAuth(
        client_id=os.environ['ZOHO_CLIENT_ID'],
        client_secret=os.environ['ZOHO_CLIENT_SECRET'],
        refresh_token=os.environ['ZOHO_REFRESH_TOKEN']
    )
    
    if not auth.get_access_token():
        print("X Authentication failed!")
        return
    
    org_id = os.environ['ZOHO_ORG_ID']
    
    print("\nFetching all categories...")
    categories_data = get_all_categories_raw(auth, org_id)
    
    if not categories_data:
        print("X Could not fetch categories")
        return
    
    print(f"\nRaw response:")
    import json
    print(json.dumps(categories_data, indent=2))
    
    # Parse and organize by department
    if 'data' in categories_data:
        ace_cats = []
        sjrrc_cats = []
        
        for cat in categories_data['data']:
            # Categories might have a departmentId or ownerId field
            dept_id = cat.get('departmentId') or cat.get('ownerId')
            
            if dept_id == ACE_DEPT_ID:
                ace_cats.append(cat)
            elif dept_id == SJRRC_DEPT_ID:
                sjrrc_cats.append(cat)
        
        print("\n" + "=" * 70)
        print("ACE DEPARTMENT CATEGORIES")
        print("=" * 70)
        for cat in sorted(ace_cats, key=lambda x: x.get('name', '')):
            print(f"{cat.get('name')}")
            print(f"  ID: {cat.get('id')}")
            print()
        
        print("\n" + "=" * 70)
        print("SJRRC DEPARTMENT CATEGORIES")
        print("=" * 70)
        for cat in sorted(sjrrc_cats, key=lambda x: x.get('name', '')):
            print(f"{cat.get('name')}")
            print(f"  ID: {cat.get('id')}")
            print()


if __name__ == "__main__":
    main()
