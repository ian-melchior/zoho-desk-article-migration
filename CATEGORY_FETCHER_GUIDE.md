# Complete Category ID Fetcher - Usage Guide

## What This Does

The new `get_all_category_ids.py` script uses Zoho Desk's **category tree API** to fetch ALL categories from both departments, including:
- ✅ Categories with articles
- ✅ Categories WITHOUT articles (empty categories)
- ✅ Complete hierarchy showing parent-child relationships
- ✅ Auto-generated mapping code for `migrator.py`

This solves your problem of not being able to find IDs for empty categories!

## How to Use

### Option 1: Run via GitHub Actions (Recommended)

1. **Push the new files to your repository:**
   ```bash
   git add get_all_category_ids.py .github/workflows/get_all_category_ids.yml
   git commit -m "Add comprehensive category ID fetcher"
   git push
   ```

2. **Run the workflow:**
   - Go to your GitHub repository
   - Click on "Actions" tab
   - Select "Get All Category IDs (Comprehensive)" workflow
   - Click "Run workflow"

3. **View the output:**
   - Click on the workflow run
   - Click on the "get-all-ids" job
   - Expand "Fetch all category IDs" step
   - See the complete category tree and mapping code

4. **Download the JSON data:**
   - Scroll to bottom of the workflow run
   - Download the "category-data" artifact
   - Contains raw JSON with all category information

### Option 2: Run Locally

```bash
# Make sure you have a .env file with your credentials
python get_all_category_ids.py
```

## What You'll Get

### 1. Complete Category Trees

The script will display both department's category structures like this:

```
================================================================================
ACE DEPARTMENT - COMPLETE CATEGORY TREE
================================================================================
Total categories: 15

📁 ACE Knowledge Base
   ID: 986740000000424001

  📁 Mobile App (under ACE Knowledge Base)
     ID: 986740000000700136

  📁 Schedule/Fares (under ACE Knowledge Base)  👈 YOUR NEW CATEGORY!
     ID: 986740000000XXXXXX

  📁 Event Trains (under ACE Knowledge Base)    👈 YOUR NEW CATEGORY!
     ID: 986740000000YYYYYY
```

### 2. Auto-Generated Mapping Code

Ready to paste into `src/migrator.py`:

```python
self.category_map = {
    '986740000000680203': '986740000000700136',  # Mobile App
    '986740000000698982': '986740000000XXXXXX',  # Schedule/Fares
    '986740000000703589': '986740000000YYYYYY',  # Event Trains
    # ... etc
}
```

### 3. JSON Data File

The script saves `category_data.json` with:
- Complete category lists for both departments
- Full tree structures
- All metadata for reference

## Next Steps After Running

1. **Locate your 5 new ACE categories** in the output:
   - Schedule/Fares
   - Event Trains  
   - Maintenance
   - Delays/Status
   - Employment

2. **Copy their IDs** from the tree display

3. **Update `src/migrator.py`**:
   - Replace the PLACEHOLDER values with real IDs
   - Or use the auto-generated mapping code
   - Example:
     ```python
     # OLD:
     '986740000000698982': 'PLACEHOLDER_SCHEDULE_FARES',
     
     # NEW:
     '986740000000698982': '986740000000XXXXXX',  # Schedule/Fares
     ```

4. **Test the migration**:
   ```bash
   # Via GitHub Actions
   Run workflow: "Test Single Article Migration"
   
   # Or locally
   python test_migrate_one.py
   ```

5. **Verify everything works**, then proceed with bulk migration!

## Troubleshooting

### "Failed to fetch ACE categories"
- Check that your root category IDs are correct in the script:
  - `ACE_ROOT_CAT_ID = '986740000000424001'`
  - `SJRRC_ROOT_CAT_ID = '986740000000262194'`
- These should match your CSV backup data

### "Authentication failed"
- Verify your GitHub secrets are set correctly
- Test authentication first with the "Test Zoho Authentication" workflow

### "No matching category found"
- Some SJRRC categories might not have exact name matches in ACE
- Manually map these by looking at the purpose/content of each category

## API Details

This script uses:
- **Endpoint**: `GET https://desk.zoho.com/api/v1/categories/{category_id}`
- **Returns**: Complete category object with nested children
- **Benefit**: Gets ALL categories regardless of article count

Unlike the old approach that relied on extracting categories from articles, this directly queries the category tree, so empty categories are included!

## Files Modified/Created

- ✅ `get_all_category_ids.py` - New comprehensive script
- ✅ `.github/workflows/get_all_category_ids.yml` - New workflow
- 📝 `src/migrator.py` - You'll update this with the IDs
- 📝 `category_data.json` - Generated when script runs (for reference)
