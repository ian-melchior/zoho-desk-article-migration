"""
Test script: Fetch a single article and inspect its structure.

This script helps us understand:
1. What fields Zoho Desk returns for an article
2. Which fields we'll need to migrate
3. The structure and format of the data

Run this to verify you can fetch articles before building the migration.
"""
import os
import json
from datetime import datetime

# Import our custom modules from the src package
from src.zoho_auth import ZohoAuth
from src.zoho_desk_api import ZohoDeskAPI


def main():
    """
    Fetch a single article and display all its details.
    """
    print("=" * 70)
    print("SINGLE ARTICLE FETCH TEST")
    print(f"Started at {datetime.now()}")
    print("=" * 70)
    
    # Step 1: Set up authentication
    print("\n[1/4] Setting up authentication...")
    
    auth = ZohoAuth(
        client_id=os.environ['ZOHO_CLIENT_ID'],
        client_secret=os.environ['ZOHO_CLIENT_SECRET'],
        refresh_token=os.environ['ZOHO_REFRESH_TOKEN']
    )
    
    # Get an access token
    if not auth.get_access_token():
        print("X Authentication failed!")
        return
    
    print("+ Authentication successful")
    
    # Step 2: Initialize API client
    print("\n[2/4] Initializing Zoho Desk API client...")
    
    api = ZohoDeskAPI(
        auth=auth,
        org_id=os.environ['ZOHO_ORG_ID']
    )
    
    print("+ API client ready")
    
    # Step 3: Fetch a single article
    print("\n[3/4] Fetching article...")
    
    # You need to provide an actual article ID from your Zoho Desk
    # Get this by:
    # 1. Log into Zoho Desk
    # 2. Go to Knowledge Base > Articles
    # 3. Click on any article
    # 4. Look at the URL - the number at the end is the article ID
    
    # For now, let's try to get the first article from the list
    articles_response = api.get_articles(limit=1)
    
    if not articles_response or not articles_response.get('data'):
        print("X No articles found or API error")
        print("Make sure you have at least one article in your Zoho Desk")
        return
    
    # Get the ID of the first article
    first_article_id = articles_response['data'][0]['id']
    print(f"+ Found article ID: {first_article_id}")
    
    # Now fetch the full details of that article
    article = api.get_article_by_id(first_article_id)
    
    if not article:
        print("X Failed to fetch article details")
        return
    
    print("+ Successfully fetched article")
    
    # Step 4: Display the article structure
    print("\n[4/4] Article details:")
    print("=" * 70)
    
    # Pretty print the entire article as JSON
    # This shows us EVERYTHING Zoho returns
    print(json.dumps(article, indent=2))
    
    print("\n" + "=" * 70)
    print("KEY FIELDS FOR MIGRATION:")
    print("=" * 70)
    
    # Highlight the fields we'll probably need for migration
    important_fields = [
        'id',
        'title',
        'answer',
        'categoryId',
        'categoryName',
        'departmentId',
        'status',
        'authorId',
        'createdTime',
        'modifiedTime',
        'viewCount',
        'likeCount',
        'dislikeCount',
        'commentCount',
        'tags',
        'attachments'
    ]
    
    print("\nFields present in this article:")
    for field in important_fields:
        if field in article:
            value = article[field]
            # Truncate long values for display
            if isinstance(value, str) and len(value) > 100:
                display_value = value[:100] + "..."
            else:
                display_value = value
            print(f"  {field}: {display_value}")
        else:
            print(f"  {field}: (not present)")
    
    # Check for any fields we might have missed
    print("\nAll fields in response:")
    print(f"  Total fields: {len(article.keys())}")
    print(f"  Fields: {', '.join(article.keys())}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Review the fields above")
    print("2. Decide which fields you need to migrate")
    print("3. Note the categoryId - you may need to map this to destination")
    print("4. Check if 'answer' field contains HTML (common in Zoho Desk)")
    print("5. Ready to move to test_migrate_one.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
