---
id: MOCK-002
status: reviewed
---
# MOCK-002 — Android internals

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **AND-Q001:** When should an Activity start and stop a visibility-dependent resource? Explain onStart/onStop versus onResume/onPause and why there is no universal answer.
2. **AND-Q002:** A Fragment observes LiveData with the Fragment as owner and updates its view binding. The view is destroyed while the Fragment remains. What can go wrong and how would you correct it?
3. **AND-Q003:** An engineer saves an unsent draft only in Activity.onDestroy. What happens when the system kills the process, and what state strategy would you choose?
4. **AND-Q004:** Compare configuration change with system-initiated process death for Activity, ViewModel and saved state. Which evidence can a pure JVM ViewSession test provide?
5. **AND-Q005:** A network response arrives after Fragment.onDestroyView. Describe an investigation, a safe rendering boundary, and tests that distinguish view cleanup from stale business state.
6. **AND-Q006:** A ViewModel preserves a form after rotation. Why does that prove nothing about process death?
7. **AND-Q007:** Review code that puts a full API response in a Bundle to survive recreation.
8. **AND-Q008:** The UI renders defaults, then saved state, then database data and visibly jumps. Design the restoration order.
9. **AND-Q009:** When is rememberSaveable useful and when should state move to a ViewModel or repository?
10. **AND-Q010:** Design tests for a checkout screen across rotation and process death.
11. **AND-Q011:** Explain why launchMode is not a substitute for modeling navigation state.
12. **AND-Q012:** An exported Activity trusts extras because only your notification creates the Intent. Review this assumption.

## Answer key

1. **AND-Q001:** I choose the boundary based on whether the resource is needed while visible or only while actively interacting. onStart/onStop often models visibility, while onResume/onPause can model foreground interaction; multi-window and API behavior matter. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q001.md)
2. **AND-Q002:** The observer may outlive the view and update or retain a stale binding. For work that renders the view, I observe using viewLifecycleOwner and clear the binding at onDestroyView, then bind the new view separately. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q002.md)
3. **AND-Q003:** onDestroy is not guaranteed on system process kill, so this is not a reliable persistence hook. I would keep a small restoration key or draft metadata in saved state as appropriate and persist durable draft content through the data layer. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q003.md)
4. **AND-Q004:** A configuration change commonly recreates an Activity and may retain a ViewModel through the owner mechanism; process death loses memory. Saved state can help reconstruct minimal UI, while durable data comes from storage. ViewSession proves only local detach/rebind behavior. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q004.md)
5. **AND-Q005:** Record the request, navigation and view lifecycle timeline. Bind rendering to the current view owner, clear old view references, and keep useful state in a longer-lived owner only if its contract requires it. Separately guard against stale responses overwriting newer state. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q005.md)
6. **AND-Q006:** ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q006.md)
7. **AND-Q007:** A Bundle is a bounded handoff, not a database. Store identity and lightweight input, then reload canonical data from the source of truth. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q007.md)
8. **AND-Q008:** Build one state reducer with explicit restoring/loading/content phases. Seed identity from saved state, read local data, and only publish states that the UI can represent honestly. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q008.md)
9. **AND-Q009:** Use it for small UI state tied to composition restoration. Hoist screen behavior to a state holder and keep durable business data in the data layer. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q009.md)
10. **AND-Q010:** Test reducer persistence separately, then Android recreation with saved state, and a fresh process-style launch that reloads durable cart identity without reusing memory fakes. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q010.md)
11. **AND-Q011:** Launch modes control Activity instance and task behavior, but they do not define business navigation or typed arguments. I model destinations and test Back from real entry points. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q011.md)
12. **AND-Q012:** Exported boundaries can be invoked externally. Validate action, origin shape, required fields, sizes, and authorization again inside the component. [Complete answer](../Interview-Question-Bank/Model-Answers/AND-Q012.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
