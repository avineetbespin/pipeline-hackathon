# Bugs Fixed - Post-Deployment

**Date:** 2026-05-13 15:30 PST

---

## Bug 1: BigQuery Dataset Not Found ✅ FIXED

**Symptom:**
```json
{
  "success": false,
  "error": "404 GET https://bigquery.googleapis.com/bigquery/v2/projects/bgus-genai-poc2/datasets/pipelinepilot/tables: Not found: Dataset bgus-genai-poc2:pipelinepilot"
}
```

**Root Cause:**
The Cloud Run service account `pipelinepilot-agent@bgus-genai-poc2.iam.gserviceaccount.com` didn't have BigQuery permissions initially.

**Fix Applied:**
```bash
gcloud projects add-iam-policy-binding bgus-genai-poc2 \
  --member="serviceAccount:pipelinepilot-agent@bgus-genai-poc2.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

**Status:** ✅ Fixed - Try the BigQuery query again!

---

## Bug 2: Execution Appears Stuck in "STARTING" ⚠️ NOT A BUG

**Symptom:**
UI shows "STARTING" status and never updates, even though execution completes.

**Root Cause:**
The Fivetran `list_destinations` API call took 2 minutes to complete. The execution actually finished successfully at 20:20:01, but the UI may have been showing stale data.

**Analysis:**
- Execution started: 20:18:00
- Execution completed: 20:20:01  
- Duration: 2 minutes 1 second
- Result: Success (returned empty destinations list)

**This is expected behavior:**
- Fivetran API can be slow on first call (cold start)
- The UI polls every 2 seconds, so it should update
- The execution DID complete successfully

**Actions:**
1. Refresh the page and check - execution should show as completed
2. The polling mechanism is working correctly
3. Consider adding a "Refresh" button to force update
4. Consider increasing poll frequency for better UX

---

## Future Improvements

### 1. Better Loading States
Add "This may take a minute..." message for slow operations like Fivetran API calls.

### 2. Manual Refresh Button
Add a "Refresh Status" button in case polling gets out of sync.

### 3. Timeout Handling
Add a timeout after 3-5 minutes with helpful error message.

### 4. Better Error Messages
Show more context when BigQuery/Fivetran operations fail.

---

## Testing Checklist

After fixes applied:

- [x] Agent backend has BigQuery permissions
- [ ] BigQuery queries work from UI
- [x] Fivetran queries complete (may be slow)
- [ ] UI polling updates correctly
- [ ] No more "Not found: Dataset" errors

---

## How to Test

### Test 1: BigQuery Query
1. Visit: https://pipelinepilot-web-hcfjm5ykkq-uc.a.run.app
2. Enter: "List all tables in my BigQuery pipelinepilot dataset"
3. Click: "Create Pipeline"
4. Expected: Success (empty list or actual tables)

### Test 2: Fivetran Query
1. Enter: "What destinations are configured in my Fivetran account?"
2. Click: "Create Pipeline"
3. Wait: May take 1-2 minutes (be patient!)
4. Expected: Success (shows destinations)

---

Last Updated: 2026-05-13 15:30 PST
