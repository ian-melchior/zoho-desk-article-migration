"""
Comprehensive Category ID Fetcher
Uses Zoho Desk's category tree API to get ALL categories, including empty ones.

This script fetches the complete category hierarchy for both departments
and displays all category IDs in a format ready to paste into migrator.py.

API Endpoint: GET /categories/{category_id}
Documentation: https://desk.zoho.com/support/APIDocument.do#KBCategory#KBCategory_Getacategorytree
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.zoho_auth import ZohoAuth


# Department IDs
ACE_DEPT_ID = '986740000000006907'
SJRRC_DEPT_ID = '986740000000403042'

# Root category IDs (from your CSV backup)
ACE_ROOT_CAT_ID = '986740000000424001'
SJRRC_ROOT_CAT_ID = '986740000000262194'


def get_category_tree(auth, org_id, category_id):
    """
    Fetch the complete category tree starting from a category ID.
    
    This uses the Zoho Desk API endpoint:
    GET /categories/{category_id}
    
    Returns the category and all its children recursively.
    """
    import requests
    
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
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch category {category_id}: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"[ERROR] Response: {e.response.text}")
        return None


def flatten_category_tree(category_data, categories_list=None, parent_name="", depth=0):
    """
    Recursively flatten a category tree into a list.
    
    Args:
        category_data (dict): Category object from API
        categories_list (list): Accumulator for flattened categories
        parent_name (str): Name of parent category for display
        depth (int): Current depth in tree
    
    Returns:
        list: Flattened list of category dicts
    """
    if categories_list is None:
        categories_list = []
    
    if not category_data:
        return categories_list
    
    # Add current category
    cat_info = {
        'id': category_data.get('id'),
        'name': category_data.get('name'),
        'parent_name': parent_name,
        'depth': depth,
        'has_children': bool(category_data.get('categories'))
    }
    categories_list.append(cat_info)
    
    # Recursively process children
    children = category_data.get('categories', [])
    for child in children:
        flatten_category_tree(
            child, 
            categories_list, 
            parent_name=category_data.get('name'),
            depth=depth + 1
        )
    
    return categories_list


def display_categories(dept_name, categories):
    """
    Display categories in a readable format with tree structure.
    """
    print(f"\n{'=' * 80}")
    print(f"{dept_name} DEPARTMENT - COMPLETE CATEGORY TREE")
    print(f"{'=' * 80}")
    print(f"Total categories: {len(categories)}")
    print()
    
    for cat in categories:
        indent = "  " * cat['depth']
        parent_info = f" (under {cat['parent_name']})" if cat['parent_name'] else ""
        children_info = " [has children]" if cat['has_children'] else ""
        
        print(f"{indent}📁 {cat['name']}{parent_info}{children_info}")
        print(f"{indent}   ID: {cat['id']}")
        print()


def create_mapping_code(sjrrc_categories, ace_categories):
    """
    Generate Python code for the category mapping in migrator.py.
    
    This helps you create the mapping by matching category names.
    """
    print(f"\n{'=' * 80}")
    print("CATEGORY MAPPING CODE FOR migrator.py")
    print(f"{'=' * 80}")
    print("\n# Copy this into src/migrator.py category_map:")
    print("self.category_map = {")
    
    # Create a lookup dict for ACE categories by name
    ace_by_name = {cat['name']: cat['id'] for cat in ace_categories}
    
    # Try to match SJRRC categories to ACE categories
    for sjrrc_cat in sjrrc_categories:
        sjrrc_name = sjrrc_cat['name']
        sjrrc_id = sjrrc_cat['id']
        
        # Look for matching name in ACE
        if sjrrc_name in ace_by_name:
            ace_id = ace_by_name[sjrrc_name]
            print(f"    '{sjrrc_id}': '{ace_id}',  # {sjrrc_name}")
        else:
            # No match found - needs manual mapping
            print(f"    '{sjrrc_id}': 'NEEDS_MAPPING',  # {sjrrc_name} -> ???")
    
    print("}")
    print("\n# Categories that need manual mapping:")
    print("# Look for similar names or decide which ACE category should receive these articles")


def main():
    print("=" * 80)
    print("COMPLETE CATEGORY ID FETCHER")
    print(f"Started at {datetime.now()}")
    print("=" * 80)
    print("\nThis script fetches ALL categories from both departments,")
    print("including empty categories, using the Zoho Desk API.")
    
    # Set up authentication
    print("\n[1/4] Authenticating...")
    auth = ZohoAuth(
        client_id=os.environ['ZOHO_CLIENT_ID'],
        client_secret=os.environ['ZOHO_CLIENT_SECRET'],
        refresh_token=os.environ['ZOHO_REFRESH_TOKEN']
    )
    
    if not auth.get_access_token():
        print("✗ Authentication failed!")
        return
    
    print("✓ Authentication successful")
    
    org_id = os.environ['ZOHO_ORG_ID']
    
    # Fetch ACE department categories
    print("\n[2/4] Fetching ACE department category tree...")
    ace_tree = get_category_tree(auth, org_id, ACE_ROOT_CAT_ID)
    
    if not ace_tree:
        print("✗ Failed to fetch ACE categories")
        return
    
    ace_categories = flatten_category_tree(ace_tree)
    print(f"✓ Found {len(ace_categories)} ACE categories")
    
    # Fetch SJRRC department categories
    print("\n[3/4] Fetching SJRRC department category tree...")
    sjrrc_tree = get_category_tree(auth, org_id, SJRRC_ROOT_CAT_ID)
    
    if not sjrrc_tree:
        print("✗ Failed to fetch SJRRC categories")
        return
    
    sjrrc_categories = flatten_category_tree(sjrrc_tree)
    print(f"✓ Found {len(sjrrc_categories)} SJRRC categories")
    
    # Display results
    print("\n[4/4] Displaying results...")
    
    display_categories("ACE", ace_categories)
    display_categories("SJRRC", sjrrc_categories)
    
    # Generate mapping code
    create_mapping_code(sjrrc_categories, ace_categories)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review the ACE categories above and find your 5 new categories:")
    print("   - Schedule/Fares")
    print("   - Event Trains")
    print("   - Maintenance")
    print("   - Delays/Status")
    print("   - Employment")
    print()
    print("2. Copy the mapping code above into src/migrator.py")
    print()
    print("3. Replace any PLACEHOLDER or NEEDS_MAPPING values with actual IDs")
    print()
    print("4. Run test_migrate_one.py to test a single article migration")
    print("=" * 80)
    
    # Save raw data to JSON for reference
    output_file = 'category_data.json'
    with open(output_file, 'w') as f:
        json.dump({
            'ace_categories': ace_categories,
            'sjrrc_categories': sjrrc_categories,
            'ace_tree': ace_tree,
            'sjrrc_tree': sjrrc_tree
        }, f, indent=2)
    
    print(f"\n✓ Raw data saved to {output_file} for reference")


if __name__ == "__main__":
    main()
