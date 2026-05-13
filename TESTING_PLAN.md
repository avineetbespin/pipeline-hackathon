# Testing Plan - Phase 4

**Target:** End-to-end UI testing with deployed services

---

## Prerequisites

**Agent Backend:** https://pipelinepilot-agent-956500419273.us-central1.run.app ✅  
**Frontend:** https://pipelinepilot-web-956500419273.us-central1.run.app ⏳

---

## Test 1: Basic Health Check

### Agent Backend
```bash
curl -k https://pipelinepilot-agent-956500419273.us-central1.run.app/health
```

**Expected:**
```json
{"status":"healthy","service":"pipelinepilot-agent","model":"gemini-3.1-pro-preview"}
```

### Frontend
```bash
curl -k https://pipelinepilot-web-956500419273.us-central1.run.app
```

**Expected:** HTML with React root div

---

## Test 2: Simple Read-Only Query

**Goal:** "Show me what Fivetran connectors I currently have"

**Expected Flow:**
1. User enters goal in text area
2. Click "Create Pipeline"
3. UI shows loading state
4. Plan appears with ~2 steps:
   - Step 1: List Fivetran groups
   - Step 2: List connectors in group
5. Steps execute automatically (no approval needed)
6. Results display in truncated JSON format
7. Execution status shows "COMPLETED"
8. Progress bar at 100%

**What to Verify:**
- Plan displays correctly
- Steps show status icons (⏳ → ⚙️ → ✓)
- Results are visible and readable
- No errors in browser console
- Polling stops when completed

---

## Test 3: Result Passing Between Steps

**Goal:** "Show me all connectors in my first Fivetran group"

**Expected Flow:**
1. Plan creates 2 steps:
   - Step 1: `list_groups()`
   - Step 2: `list_connectors(group_id="{{step_0.data.items[0].id}}")`
2. Step 1 executes, returns group data
3. Step 2's arguments show RESOLVED group_id (not `{{...}}` placeholder)
4. Step 2 executes successfully with actual group ID
5. Results show connectors from that specific group

**What to Verify:**
- Step 2 arguments show resolved value: `"predicament_glisten"` (not placeholder)
- Step 2 executes without error
- Result contains connector list for correct group
- Browser console shows "Resolved reference" log (if debug enabled)

---

## Test 4: Approval Gate (Write Operation)

**Goal:** "Create a test BigQuery view"

**Expected Flow:**
1. Plan creates steps including a write operation
2. Step with `requires_approval: true` shows yellow approval UI
3. Approval gate displays:
   - "Approval Required" heading
   - Tool name and arguments
   - Cost estimate (if available)
   - Green "Approve" button
   - Red "Reject" button
4. Clicking "Approve":
   - Button shows "Approving..."
   - Step proceeds to execution
   - Status changes to in_progress → completed
5. Clicking "Reject":
   - Shows reason input field
   - "Confirm Rejection" button
   - Step fails with rejection reason

**What to Verify:**
- Approval UI appears for write operations
- Approve button triggers execution
- Reject button prevents execution
- Status updates reflect approval decision
- Can't approve same step twice

---

## Test 5: Multi-Step Plan with Mixed Operations

**Goal:** "List my Fivetran groups and then show the first connector's schema"

**Expected Flow:**
1. Plan with 3+ steps
2. Multiple result passing operations
3. Mix of read and potential write operations
4. Execution proceeds step-by-step
5. Can scroll through plan while execution runs
6. ExecutionStatus component updates in real-time

**What to Verify:**
- Complex plans execute correctly
- Multiple result references resolve
- UI remains responsive during execution
- Progress bar updates smoothly
- Step details expand/collapse properly

---

## Test 6: Error Handling

### Invalid Goal
**Goal:** "asdfghjkl random nonsense"

**Expected:**
- Gemini still creates a plan (or returns error)
- Error message displays in red banner
- Can click "New Pipeline" to reset

### Failed Step
**Goal:** Trigger a connector ID that doesn't exist

**Expected:**
- Step shows failed status (red)
- Error message displays under step
- Execution stops at failed step
- Subsequent steps remain pending
- Overall status shows "FAILED"

**What to Verify:**
- Error messages are clear and helpful
- Failed steps are visually distinct
- Can recover with "New Pipeline" button
- No uncaught exceptions in console

---

## Test 7: UI/UX Quality

### Desktop Experience
- [ ] Layout is clean and professional
- [ ] Colors and spacing are consistent
- [ ] Buttons have hover states
- [ ] Loading spinners are smooth
- [ ] Text is readable (font size, contrast)
- [ ] Scrolling works correctly

### Mobile/Responsive
- [ ] UI adapts to narrow screens
- [ ] Buttons remain tappable
- [ ] Text doesn't overflow
- [ ] Two-column layout stacks vertically

### Performance
- [ ] Initial page load < 3 seconds
- [ ] Plan creation < 5 seconds
- [ ] Step execution feels responsive
- [ ] No UI jank during polling

---

## Test 8: Example Prompts

Test each example prompt from the UI:

1. "Show me what Fivetran connectors I currently have set up"
   - Expected: 2-3 steps, lists connectors, completes in <10s

2. "List all tables in my BigQuery pipelinepilot dataset"
   - Expected: 1-2 steps, calls BigQuery API, shows tables

3. "What destinations are configured in my Fivetran account?"
   - Expected: 1-2 steps, lists BigQuery destination

---

## Test 9: Concurrent Executions

1. Start execution A
2. Open new browser tab
3. Start execution B
4. Both should execute independently
5. Each tab polls its own execution

**What to Verify:**
- In-memory state doesn't collide
- Each execution has unique ID
- Results don't mix between tabs

---

## Test 10: Browser Compatibility

Test in:
- [ ] Chrome (primary)
- [ ] Firefox
- [ ] Edge
- [ ] Safari (if available)

**What to Verify:**
- UI renders correctly
- Fetch API works
- Polling mechanism works
- No browser-specific CSS issues

---

## Success Criteria

**All tests must:**
- Execute without errors
- Display results correctly
- Handle failures gracefully
- Provide clear feedback to user

**Phase 4 Complete When:**
- ✅ Agent backend deployed with result passing
- ✅ Frontend deployed and accessible
- ✅ Tests 1-5 passing
- ✅ No critical bugs
- ✅ UI is polished and professional

---

## Known Limitations (Expected)

1. **In-memory state** - Lost on backend restart (acceptable for MVP)
2. **No persistence** - Execution history not saved (Phase 5)
3. **No authentication** - Public access (acceptable for demo)
4. **No cost estimates** - Shows placeholder text (Phase 4 TODO)
5. **No reasoning toggle** - T4.5 not yet implemented

---

## Debug Tools

### Browser Console
```javascript
// Check API endpoint
console.log(import.meta.env.VITE_API_URL)

// Manually test API
fetch('https://pipelinepilot-agent-956500419273.us-central1.run.app/health')
  .then(r => r.json())
  .then(console.log)
```

### Network Tab
- Check request/response payloads
- Verify polling happens every 2 seconds
- Check for 4xx/5xx errors

### React DevTools
- Inspect component state
- Check prop flow
- Monitor re-renders

---

Last Updated: 2026-05-13 14:50 PST
