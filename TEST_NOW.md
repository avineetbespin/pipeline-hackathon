# 🧪 Test PipelinePilot NOW

**All services updated and ready!**  
**Agent redeployed:** ✅ Result passing fixed  
**Sample data:** ✅ 3 tables with realistic data  
**UI:** ✅ Live and functional

---

## 🚀 Open the UI

**https://pipelinepilot-web-hcfjm5ykkq-uc.a.run.app**

---

## ✅ Test 1: Simple BigQuery Query

**Enter this:**
```
List all tables in pipelinepilot
```

**Expected Result:**
- Plan with 1 step
- Completes in <5 seconds
- Shows 3 tables:
  - connectors
  - sync_logs
  - revenue_summary
- Status: COMPLETED

---

## ✅ Test 2: Query with Data

**Enter this:**
```
Show me the latest sync logs
```

**Expected Result:**
- Plan with 1-2 steps
- Returns 4 sync records
- Shows:
  - sync_id
  - connector_name
  - rows_synced
  - status
- All marked as "success"

---

## ✅ Test 3: Result Passing (Multi-Step)

**Enter this:**
```
Show me all connectors in my first Fivetran group
```

**Expected Result:**
- Plan with 2 steps:
  - Step 1: list_groups()
  - Step 2: list_connectors(group_id=**ACTUAL_VALUE**)
- **Key verification:** Step 2 arguments should show:
  ```json
  {"group_id": "predicament_glisten"}
  ```
  **NOT:**
  ```json
  {"group_id": "<group_id_from_step_1>"}
  ```
- Status: COMPLETED
- Both steps show green checkmarks

**This proves result passing is working!**

---

## ✅ Test 4: Query Sample Data

**Enter this:**
```
Show me connector status
```

**Expected Result:**
- Returns 3 connectors:
  - Stripe Production (stripe)
  - HubSpot CRM (hubspot)
  - Google Ads Main (google_ads)
- All status: "active"
- Created dates in May 2026

---

## ✅ Test 5: Aggregation Query

**Enter this:**
```
What is the total revenue from Stripe?
```

**Expected Result:**
- SQL query against revenue_summary table
- Returns: $69,715.30 (sum of 4 days)
- Or shows individual daily revenue

---

## ⚠️ Test 6: Slow Fivetran Query

**Enter this:**
```
What destinations are configured in my Fivetran account?
```

**Expected Behavior:**
- Plan with 1 step
- Step starts immediately
- **Takes 2-5 minutes** (Fivetran API is slow)
- Status shows "IN_PROGRESS" for a while
- Eventually completes with SUCCESS
- Returns destinations list

**Be patient!** This is expected. The UI should keep polling and update when complete.

---

## 🐛 Known Issues

### Issue 1: Fivetran Takes Forever
- **Status:** Expected behavior
- **Why:** Fivetran API cold start
- **What to do:** Be patient, refresh page if needed after 5 min

### Issue 2: UI Doesn't Update
- **Status:** Polling issue
- **What to do:** Manual page refresh
- **Fix needed:** Better polling + manual refresh button

### Issue 3: Results Truncated
- **Status:** By design (shows first 300 chars)
- **What to do:** Scroll or check full result in status panel
- **Fix needed:** Expandable JSON view

---

## 📊 What You Should See

### Good Results:
```json
{
  "success": true,
  "table_count": 3,
  "tables": [
    {"table_id": "connectors", "table_type": "TABLE"},
    {"table_id": "sync_logs", "table_type": "TABLE"},
    {"table_id": "revenue_summary", "table_type": "TABLE"}
  ]
}
```

### Result Passing Working:
```
Step 1: Completed
  Result: {"data": {"items": [{"id": "predicament_glisten"}]}}

Step 2: In Progress
  Arguments: {"group_id": "predicament_glisten"}  ← RESOLVED!
```

### Bad Results (Report These):
- Placeholders still showing: `<group_id_from_step_1>`
- Errors: 404, 500, timeout
- UI stuck: No updates after 5+ minutes
- Wrong data: Unexpected results

---

## 🎯 Success Criteria

**Phase 4 is successful if:**
- ✅ BigQuery queries return data instantly
- ✅ Result passing works (no placeholders)
- ✅ Multi-step plans complete
- ✅ Fivetran queries complete (even if slow)
- ✅ UI shows progress and results
- ✅ No critical errors

---

## 🔧 If Something Breaks

### 1. Check Agent Health
```bash
curl https://pipelinepilot-agent-956500419273.us-central1.run.app/health
```
Should return: `{"status":"healthy",...}`

### 2. Check Recent Logs
```bash
gcloud run services logs read pipelinepilot-agent \
  --region=us-central1 \
  --project=bgus-genai-poc2 \
  --limit=20
```

### 3. Refresh Everything
- Close all browser tabs
- Clear cache (Ctrl+Shift+Delete)
- Open fresh: https://pipelinepilot-web-hcfjm5ykkq-uc.a.run.app

### 4. Check Build Status
```bash
gcloud builds list --limit=1 --project=bgus-genai-poc2
```
Should show: STATUS = SUCCESS

---

## 📝 Test Results Template

**Copy this and fill it out:**

```
TEST RESULTS - [DATE/TIME]

Test 1 - Simple BigQuery: [PASS/FAIL]
  - Duration: _____ seconds
  - Tables returned: _____

Test 2 - Query with Data: [PASS/FAIL]
  - Records returned: _____
  - Data looks correct: [YES/NO]

Test 3 - Result Passing: [PASS/FAIL]
  - Step 2 showed actual value: [YES/NO]
  - No placeholders: [YES/NO]

Test 4 - Sample Data: [PASS/FAIL]
  - Connectors count: _____

Test 5 - Aggregation: [PASS/FAIL]
  - Total revenue: $_____

Test 6 - Fivetran Query: [PASS/FAIL/TIMEOUT]
  - Duration: _____ minutes
  - Result: [SUCCESS/FAILURE]

OVERALL: [PASS/FAIL]
Notes: ___________
```

---

## 🎉 Success!

**If all tests pass, you have:**
- ✅ Fully functional AI agent
- ✅ Result passing working
- ✅ Real data to query
- ✅ Multi-step workflows
- ✅ Production deployment

**Ready for:**
- Demo to stakeholders
- Recording demo video
- Phase 5 (hardening)
- Phase 6 (submission)

---

**Start testing now:**  
https://pipelinepilot-web-hcfjm5ykkq-uc.a.run.app

Last Updated: 2026-05-13 16:00 PST
