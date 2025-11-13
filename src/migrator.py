"""
Migration logic for Zoho Desk articles.
Handles category mapping and article transformation.
"""


class ArticleMigrator:
    """
    Handles the migration of articles between departments.
    
    This class:
    - Maps category IDs from source to destination
    - Transforms article data for creation in destination
    - Tracks migration results
    """
    
    def __init__(self, source_api, destination_api=None):
        """
        Initialize the migrator.
        
        Args:
            source_api (ZohoDeskAPI): API client for source department
            destination_api (ZohoDeskAPI): API client for destination department
                                           If None, uses same as source (same org)
        """
        self.source_api = source_api
        self.destination_api = destination_api or source_api
        self.migration_log = []
        
        # Category mapping: SJRRC category ID -> ACE category ID
        # This maps categories by name based on your current structure
        # Format: 'source_category_id': 'destination_category_id'
        self.category_map = {
            # Direct matches under root
            '986740000000680203': '986740000000700136',  # Mobile App
            '986740000000680258': '986740000000700114',  # Ticketing
            '986740000000682002': '986740000000700125',  # Wi-Fi
            '986740000000688053': '986740000000700147',  # Test Rides
            '986740000000698100': '986740000000700158',  # Group Travel
            '986740000000698209': '986740000000700169',  # Bikes
            '986740000000262213': '986740000000424018',  # General
            
            # These are already in ACE (no mapping needed, same category)
            '986740000000698448': '986740000000698448',  # ADA
            '986740000000698752': '986740000000698752',  # Safety and Security
            '986740000000698851': '986740000000698851',  # Service Alerts
            
            # Internal Communications sub-categories
            # NOTE: You'll need to get the actual IDs for the 5 new categories you created
            # For now, these are placeholders - update after creating categories
            '986740000000698982': 'PLACEHOLDER_SCHEDULE_FARES',     # Schedule/Fares
            '986740000000703267': 'PLACEHOLDER_DELAYS_STATUS',      # Delays/Status
            '986740000000703324': '986740000000700136',             # Mobile App (under Internal Comms)
            '986740000000703347': '986740000000700114',             # Ticketing (under Internal Comms)
            '986740000000703534': '986740000000700169',             # Bikes (under Internal Comms)
            '986740000000703589': 'PLACEHOLDER_EVENT_TRAINS',       # Event Trains
            '986740000000703694': 'PLACEHOLDER_EMPLOYMENT',         # Employment
            '986740000000716054': 'PLACEHOLDER_MAINTENANCE',        # Maintenance
        }
    
    def map_category_id(self, source_category_id):
        """
        Map a source category ID to destination category ID.
        
        Args:
            source_category_id (str): Category ID from source department
            
        Returns:
            str: Mapped category ID for destination, or None if no mapping
        """
        mapped_id = self.category_map.get(source_category_id)
        
        if not mapped_id:
            print(f"[Migrator] WARNING: No mapping found for category ID {source_category_id}")
            return None
        
        if mapped_id.startswith('PLACEHOLDER_'):
            print(f"[Migrator] ERROR: Category mapping is a placeholder: {mapped_id}")
            print(f"[Migrator] You need to create this category in ACE and update the mapping")
            return None
        
        return mapped_id
    
    def transform_article(self, source_article, destination_department_id):
        """
        Transform a source article for creation in destination department.
        
        This extracts the fields needed to create a new article and maps
        category IDs appropriately.
        
        Args:
            source_article (dict): Complete article from source
            destination_department_id (str): Target department ID
            
        Returns:
            dict: Transformed article data ready for creation, or None if error
        """
        # Map the category ID
        source_category_id = source_article.get('categoryId')
        destination_category_id = self.map_category_id(source_category_id)
        
        if not destination_category_id:
            return None
        
        # Build the new article data
        # Only include fields that the API accepts for creation
        transformed = {
            'title': source_article.get('title'),
            'answer': source_article.get('answer'),
            'categoryId': destination_category_id,
            'departmentId': destination_department_id,
        }
        
        # Optional fields - include if present
        if 'status' in source_article:
            transformed['status'] = source_article.get('status')
        
        # Tags - preserve if present
        if 'tags' in source_article and source_article['tags']:
            transformed['tags'] = source_article['tags']
        
        # Summary/excerpt - preserve if present
        if 'summary' in source_article and source_article['summary']:
            transformed['summary'] = source_article['summary']
        
        return transformed
    
    def migrate_single_article(self, article_id, destination_department_id, dry_run=False):
        """
        Migrate a single article from source to destination.
        
        Args:
            article_id (str): Source article ID to migrate
            destination_department_id (str): Target department ID
            dry_run (bool): If True, only show what would happen without creating
            
        Returns:
            dict: Migration result with status and details
        """
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating article {article_id}...")
        
        # Fetch the source article
        source_article = self.source_api.get_article_by_id(article_id)
        
        if not source_article:
            result = {
                'article_id': article_id,
                'status': 'failed',
                'error': 'Failed to fetch source article'
            }
            self.migration_log.append(result)
            return result
        
        print(f"[Migrator] Source article: {source_article.get('title')}")
        print(f"[Migrator] Source category ID: {source_article.get('categoryId')}")
        print(f"[Migrator] Source department ID: {source_article.get('departmentId')}")
        
        # Check for tags
        tags = source_article.get('tags', [])
        if tags:
            print(f"[Migrator] Tags: {', '.join(tags)}")
        else:
            print(f"[Migrator] No tags found")
        
        # Transform the article
        transformed = self.transform_article(source_article, destination_department_id)
        
        if not transformed:
            result = {
                'article_id': article_id,
                'title': source_article.get('title'),
                'status': 'failed',
                'error': 'Category mapping failed'
            }
            self.migration_log.append(result)
            return result
        
        print(f"[Migrator] Destination category ID: {transformed['categoryId']}")
        print(f"[Migrator] Destination department ID: {transformed['departmentId']}")
        
        if dry_run:
            result = {
                'article_id': article_id,
                'title': source_article.get('title'),
                'status': 'dry_run',
                'source': source_article,
                'transformed': transformed
            }
            self.migration_log.append(result)
            return result
        
        # Create the article in destination
        created_article = self.destination_api.create_article(transformed)
        
        if created_article:
            result = {
                'article_id': article_id,
                'title': source_article.get('title'),
                'status': 'success',
                'new_article_id': created_article.get('id'),
                'new_permalink': created_article.get('permalink')
            }
            print(f"[Migrator] SUCCESS! New article ID: {created_article.get('id')}")
            print(f"[Migrator] Permalink: {created_article.get('permalink')}")
        else:
            result = {
                'article_id': article_id,
                'title': source_article.get('title'),
                'status': 'failed',
                'error': 'API creation failed'
            }
        
        self.migration_log.append(result)
        return result
