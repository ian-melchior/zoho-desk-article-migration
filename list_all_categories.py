"""
List ALL categories by fetching the category tree for each department.
Uses the correct Zoho Desk API endpoints.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

from src.zoho_auth import ZohoAuth


ACE_DEPT_ID = '986740000000006907'
SJRRC_DEPT_ID = '986740000000403042'

# Root category IDs from your CSV backup
ACE_ROOT_CAT_ID = '986740000000424001'
SJRRC_ROOT_CAT_ID = '986740000000262194'


def get_category_tree(auth, org_id, category_id):
    """
    Fetch category tree for a specific category.
    """
    if not auth.access_token:
        auth.get_access_token()
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {auth.access_token}",
        "orgId": org_id
    }
    
    url = f"https://desk.zoho.com/api/v1/categories/{category_id}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching category {category_id}: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None


def print_category_tree(category_data, indent=0):
    """
    Recursively print category tree.
    """
    if not category_data:
        return
    
    name = category_data.get('name', 'Unknown')
    cat_id = category_data.get('id', 'Unknown')
    
    print("  " * indent + f"{name}")
    print("  " * indent + f"  ID: {cat_id}")
    
    # Check for child categories
    if 'categories' in category_data and category_data['categories']:
        for child in category_data['categories']:
            print_category_tree(child, indent + 1)


def main():
    print("=" * 70)
    print("COMPLETE CATEGORY TREE LISTING")
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
    
    print("\n" + "=" * 70)
    print("ACE DEPARTMENT CATEGORY TREE")
    print("=" * 70)
    ace_tree = get_category_tree(auth, org_id, ACE_ROOT_CAT_ID)
    if ace_tree:
        print_category_tree(ace_tree)
    
    print("\n" + "=" * 70)
    print("SJRRC DEPARTMENT CATEGORY TREE")
    print("=" * 70)
    sjrrc_tree = get_category_tree(auth, org_id, SJRRC_ROOT_CAT_ID)
    if sjrrc_tree:
        print_category_tree(sjrrc_tree)
    
    print("\n" + "=" * 70)
    print("CATEGORY MAPPING GUIDE")
    print("=" * 70)
    print("\nNow match the category names between ACE and SJRRC")
    print("and note which SJRRC IDs map to which ACE IDs.")


if __name__ == "__main__":
    main()
