"""
Test script: Migrate a single article from SJRRC to ACE department.

This script:
1. Fetches one article from SJRRC department (with all fields including tags)
2. Shows the complete source article data
3. Transforms it for the ACE department
4. Creates a duplicate in ACE (or shows what would be created in dry run mode)
5. Verifies the migration was successful

Run with dry_run=True first to see what would happen without actually creating.
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from src.zoho_auth import ZohoAuth
from src.zoho_desk_api import ZohoDeskAPI
from src.migrator import ArticleMigrator


# Department IDs from your Zoho Desk
SJRRC_DEPARTMENT_ID = '986740000000403042'
ACE_DEPARTMENT_ID = '986740000000006907'


def main():
    """
    Test migration of a single article.
    """
    print("=" * 70)
    print("SINGLE ARTICLE MIGRATION TEST")
    print(f"Started at {datetime.now()}")
    print("=" * 70)
    
    # Step 1: Set up authentication
    print("\n[1/6] Setting up authentication...")
    
    auth = ZohoAuth(
        client_id=os.environ['ZOHO_CLIENT_ID'],
        client_secret=os.environ['ZOHO_CLIENT_SECRET'],
        refresh_token=os.environ['ZOHO_REFRESH_TOKEN']
    )
    
    if not auth.get_access_token():
        print("X Authentication failed!")
        return
    
    print("+ Authentication successful")
    
    # Step 2: Initialize API client
    print("\n[2/6] Initializing Zoho Desk API client...")
    
    api = ZohoDeskAPI(
        auth=auth,
        org_id=os.environ['ZOHO_ORG_ID']
    )
    
    print("+ API client ready")
    
    # Step 3: Get a test article from SJRRC department
    print("\n[3/6] Fetching articles from SJRRC department...")
    
    # Get articles from SJRRC department
    # We'll fetch a few and let you pick one
    articles_response = api.get_articles(limit=5)
    
    if not articles_response or not articles_response.get('data'):
        print("X No articles found")
        return
    
    # Filter for SJRRC department articles
    sjrrc_articles = [
        a for a in articles_response['data'] 
        if a.get('departmentId') == SJRRC_DEPARTMENT_ID
    ]
    
    if not sjrrc_articles:
        print("X No SJRRC articles found in first 5 results")
        print("Trying to fetch more...")
        articles_response = api.get_articles(limit=20)
        sjrrc_articles = [
            a for a in articles_response.get('data', [])
            if a.get('departmentId') == SJRRC_DEPARTMENT_ID
        ]
    
    if not sjrrc_articles:
        print("X Still no SJRRC articles found")
        return
    
    print(f"+ Found {len(sjrrc_articles)} SJRRC articles")
    print("\nAvailable articles:")
    for i, article in enumerate(sjrrc_articles[:5], 1):
        print(f"  {i}. [{article['id']}] {article.get('title', 'Untitled')}")
    
    # Use the first one for testing
    test_article_id = sjrrc_articles[0]['id']
    print(f"\n+ Using article: {test_article_id}")
    
    # Step 4: Fetch complete article details
    print("\n[4/6] Fetching complete article details...")
    
    full_article = api.get_article_by_id(test_article_id)
    
    if not full_article:
        print("X Failed to fetch full article")
        return
    
    print("+ Article fetched successfully")
    print(f"\nArticle details:")
    print(f"  Title: {full_article.get('title')}")
    print(f"  Category ID: {full_article.get('categoryId')}")
    print(f"  Department ID: {full_article.get('departmentId')}")
    print(f"  Status: {full_article.get('status')}")
    print(f"  Tags: {full_article.get('tags', [])}")
    print(f"  Created: {full_article.get('createdTime')}")
    
    # Show first 200 chars of content
    answer = full_article.get('answer', '')
    if len(answer) > 200:
        print(f"  Content preview: {answer[:200]}...")
    else:
        print(f"  Content: {answer}")
    
    # Step 5: Initialize migrator and test transformation
    print("\n[5/6] Testing article transformation...")
    
    migrator = ArticleMigrator(
        source_api=api,
        destination_api=api  # Same org, different department
    )
    
    # First do a dry run to see what would be created
    print("\n--- DRY RUN (no actual creation) ---")
    dry_run_result = migrator.migrate_single_article(
        article_id=test_article_id,
        destination_department_id=ACE_DEPARTMENT_ID,
        dry_run=True
    )
    
    if dry_run_result['status'] != 'dry_run':
        print(f"\nX Dry run failed: {dry_run_result.get('error')}")
        print("\nTroubleshooting:")
        print("  1. Check that you created all 5 missing categories in ACE")
        print("  2. Update the PLACEHOLDER values in src/migrator.py with real category IDs")
        return
    
    print("\n+ Transformation successful!")
    print("\nTransformed article data:")
    print(json.dumps(dry_run_result['transformed'], indent=2))
    
    # Step 6: Ask user if they want to actually create the article
    print("\n[6/6] Ready to create article in ACE department")
    print("\n" + "=" * 70)
    print("READY TO MIGRATE")
    print("=" * 70)
    print(f"Source: {full_article.get('title')}")
    print(f"From: SJRRC department")
    print(f"To: ACE department")
    print(f"Category mapping verified: Yes")
    print("=" * 70)
    
    # For GitHub Actions, we'll default to NOT creating (just dry run)
    # When running locally, you can change this to True
    actually_create = False
    
    if actually_create:
        print("\nCreating article in ACE department...")
        
        result = migrator.migrate_single_article(
            article_id=test_article_id,
            destination_department_id=ACE_DEPARTMENT_ID,
            dry_run=False
        )
        
        if result['status'] == 'success':
            print("\n+ SUCCESS! Article migrated successfully")
            print(f"New article ID: {result['new_article_id']}")
            print(f"Permalink: {result['new_permalink']}")
            print("\nNext steps:")
            print("  1. Verify the article appears in ACE knowledge base")
            print("  2. Check the URL works correctly")
            print("  3. If successful, proceed to batch migration")
        else:
            print(f"\nX Migration failed: {result.get('error')}")
    else:
        print("\nDRY RUN ONLY - No article was created")
        print("\nTo actually create the article:")
        print("  1. Review the transformed data above")
        print("  2. Set actually_create = True in the script")
        print("  3. Run again")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
