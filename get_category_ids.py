"""
Utility script: List all categories in ACE department with their IDs.
This helps us get the category IDs for the newly created categories.
"""
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.zoho_auth import ZohoAuth
from src.zoho_desk_api import ZohoDeskAPI


def get_all_categories(api):
    """
    Fetch all categories from Zoho Desk.
    Note: This uses an undocumented endpoint - may need adjustment.
    """
    # Try to get categories - the endpoint might be /categories or /kb/categories
    headers = api._get_headers()
    
    # Try the articles endpoint and extract unique categories
    articles = api.get_articles()
    
    if not articles or not articles.get('data'):
        return None
    
    # Extract unique category info from articles
    categories = {}
    for article in articles['data']:
        cat_id = article.get('categoryId')
        cat_name = article.get('category', {}).get('name') if isinstance(article.get('category'), dict) else None
        dept_id = article.get('departmentId')
        
        if cat_id and cat_id not in categories:
            categories[cat_id] = {
                'id': cat_id,
                'name': cat_name,
                'department_id': dept_id
            }
    
    return categories


def main():
    print("=" * 70)
    print("CATEGORY ID FINDER")
    print(f"Started at {datetime.now()}")
    print("=" * 70)
    
    # Set up authentication
    print("\nAuthenticating...")
    auth = ZohoAuth(
        client_id=os.environ['ZOHO_CLIENT_ID'],
        client_secret=os.environ['ZOHO_CLIENT_SECRET'],
        refresh_token=os.environ['ZOHO_REFRESH_TOKEN']
    )
    
    if not auth.get_access_token():
        print("X Authentication failed!")
        return
    
    # Initialize API
    api = ZohoDeskAPI(
        auth=auth,
        org_id=os.environ['ZOHO_ORG_ID']
    )
    
    print("\nFetching articles to extract category information...")
    
    # Get articles from both departments
    articles_response = api.get_articles()
    
    if not articles_response:
        print("X Failed to fetch articles")
        return
    
    # Department IDs
    ACE_DEPT = '986740000000006907'
    SJRRC_DEPT = '986740000000403042'
    
    # Extract categories by department
    ace_categories = {}
    sjrrc_categories = {}
    
    for article in articles_response.get('data', []):
        cat_id = article.get('categoryId')
        dept_id = article.get('departmentId')
        
        # Try to get category name from the article's category object
        cat_name = None
        if 'category' in article and isinstance(article['category'], dict):
            cat_name = article['category'].get('name')
        
        if dept_id == ACE_DEPT and cat_id:
            if cat_id not in ace_categories:
                ace_categories[cat_id] = {
                    'name': cat_name or 'Unknown',
                    'article_count': 0
                }
            ace_categories[cat_id]['article_count'] += 1
        
        elif dept_id == SJRRC_DEPT and cat_id:
            if cat_id not in sjrrc_categories:
                sjrrc_categories[cat_id] = {
                    'name': cat_name or 'Unknown',
                    'article_count': 0
                }
            sjrrc_categories[cat_id]['article_count'] += 1
    
    print("\n" + "=" * 70)
    print("ACE DEPARTMENT CATEGORIES")
    print("=" * 70)
    for cat_id, info in sorted(ace_categories.items(), key=lambda x: x[1]['name']):
        print(f"{info['name']}")
        print(f"  ID: {cat_id}")
        print(f"  Articles: {info['article_count']}")
        print()
    
    print("\n" + "=" * 70)
    print("SJRRC DEPARTMENT CATEGORIES")
    print("=" * 70)
    for cat_id, info in sorted(sjrrc_categories.items(), key=lambda x: x[1]['name']):
        print(f"{info['name']}")
        print(f"  ID: {cat_id}")
        print(f"  Articles: {info['article_count']}")
        print()
    
    print("\n" + "=" * 70)
    print("CATEGORY MAPPING FOR src/migrator.py")
    print("=" * 70)
    print("\nLook for the 5 new categories you created:")
    print("  - Schedule/Fares")
    print("  - Event Trains")
    print("  - Maintenance")
    print("  - Delays/Status")
    print("  - Employment")
    print("\nIf they don't appear above, they might not have any articles yet.")
    print("In that case, create a test article in each category, then run this again.")


if __name__ == "__main__":
    main()
