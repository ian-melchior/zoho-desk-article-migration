# Quick Start Checklist - Get Category IDs

## Immediate Next Steps

### ✅ Step 1: Add the New Script to Your Repo
```bash
# From your local repo directory:
git add get_all_category_ids.py
git add .github/workflows/get_all_category_ids.yml
git commit -m "Add comprehensive category ID fetcher using Zoho API"
git push
```

### ✅ Step 2: Run the Workflow
1. Go to: https://github.com/YOUR-USERNAME/zoho-desk-article-migration/actions
2. Click "Get All Category IDs (Comprehensive)"
3. Click "Run workflow" → "Run workflow"
4. Wait ~30 seconds

### ✅ Step 3: View the Results
1. Click on the workflow run
2. Click "get-all-ids" job
3. Expand "Fetch all category IDs" step
4. **Copy the entire output** (you'll need it!)

### ✅ Step 4: Find Your 5 New Category IDs
Look in the ACE category tree output for:
- [ ] Schedule/Fares
- [ ] Event Trains
- [ ] Maintenance
- [ ] Delays/Status
- [ ] Employment

Write down their IDs:
```
Schedule/Fares:  986740000000______
Event Trains:    986740000000______
Maintenance:     986740000000______
Delays/Status:   986740000000______
Employment:      986740000000______
```

### ✅ Step 5: Update migrator.py
1. Open `src/migrator.py`
2. Find the `self.category_map` dictionary
3. Replace the PLACEHOLDER values:

**BEFORE:**
```python
'986740000000698982': 'PLACEHOLDER_SCHEDULE_FARES',
'986740000000703267': 'PLACEHOLDER_DELAYS_STATUS',
'986740000000703589': 'PLACEHOLDER_EVENT_TRAINS',
'986740000000703694': 'PLACEHOLDER_EMPLOYMENT',
'986740000000716054': 'PLACEHOLDER_MAINTENANCE',
```

**AFTER:**
```python
'986740000000698982': '986740000000______',  # Schedule/Fares
'986740000000703267': '986740000000______',  # Delays/Status
'986740000000703589': '986740000000______',  # Event Trains
'986740000000703694': '986740000000______',  # Employment
'986740000000716054': '986740000000______',  # Maintenance
```

4. Save the file
5. Commit and push:
```bash
git add src/migrator.py
git commit -m "Update category mappings with actual ACE category IDs"
git push
```

### ✅ Step 6: Test Single Article Migration
1. Go to Actions → "Test Single Article Migration"
2. Click "Run workflow"
3. Check the output - should show:
   - ✅ Article fetched successfully
   - ✅ Category mapping successful (no PLACEHOLDER errors!)
   - ✅ Transformation complete
   - ✅ Dry run successful

### ✅ Step 7: Actually Migrate One Article
1. Edit `test_migrate_one.py` locally
2. Change line: `actually_create = False` → `actually_create = True`
3. Run: `python test_migrate_one.py`
4. Verify the new article appears in ACE department
5. Check all fields copied correctly (title, content, tags, etc.)

### ✅ Step 8: Prepare for Bulk Migration
Once single article test passes:
1. Create a list of all SJRRC article IDs to migrate
2. Create a batch migration script
3. Test with a small batch (5-10 articles)
4. Run full migration
5. Verify all articles migrated correctly

## Troubleshooting

### ❌ "No mapping found for category ID"
- You missed updating a PLACEHOLDER value
- Go back to Step 5 and double-check all 5 categories

### ❌ "Category mapping is a placeholder"
- Same as above - check migrator.py for any remaining PLACEHOLDER_ values

### ❌ "Failed to fetch ACE categories"
- Check root category IDs in `get_all_category_ids.py`:
  - ACE_ROOT_CAT_ID = '986740000000424001'
  - SJRRC_ROOT_CAT_ID = '986740000000262194'
- Verify these match your setup

### ❌ "Authentication failed"
- Run "Test Zoho Authentication" workflow first
- Check GitHub secrets are set correctly

## Expected Timeline

- **Step 1-2:** 5 minutes (add files, run workflow)
- **Step 3-4:** 2 minutes (review output, note IDs)
- **Step 5:** 3 minutes (update migrator.py)
- **Step 6:** 2 minutes (test dry run)
- **Step 7:** 5 minutes (test real migration)
- **Total:** ~15-20 minutes to be fully ready for bulk migration!

## Success Criteria

You're ready for bulk migration when:
- ✅ All 5 category IDs found and mapped
- ✅ No PLACEHOLDER values remaining in migrator.py
- ✅ Test migration dry run succeeds
- ✅ Test migration actual creation succeeds
- ✅ Test article appears correctly in ACE department
- ✅ All article fields preserved (title, content, tags, etc.)

---

## Quick Reference

**New Script:** `get_all_category_ids.py`
**Workflow:** `.github/workflows/get_all_category_ids.yml`
**File to Update:** `src/migrator.py` (category_map dictionary)
**Test Script:** `test_migrate_one.py`

**Documentation:**
- Full guide: `CATEGORY_FETCHER_GUIDE.md`
- Comparison: `COMPARISON.md`

Good luck! You're very close to completing this migration. 🚀
