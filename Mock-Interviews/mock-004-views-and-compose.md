---
id: MOCK-004
status: reviewed
---
# MOCK-004 — Views and Compose

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **UI-Q001:** Explain what LayoutManager, Adapter and ViewHolder each do in RecyclerView. Which part owns row identity for a diff?
2. **UI-Q002:** A note keeps ID n-1 but changes title from old to new. What should areItemsTheSame and areContentsTheSame return, and why?
3. **UI-Q003:** An adapter submits a mutable list, then a caller edits that same list in place and the UI does not update reliably. Diagnose and correct the boundary.
4. **UI-Q004:** A Fragment holds its view binding in a field and observes list state using the Fragment as LifecycleOwner. What risk appears after onDestroyView?
5. **UI-Q005:** The NoteRow unit tests pass. Which RecyclerView claims can you make, and which require AndroidX or device tests?
6. **UI-Q006:** A senior review exposes this failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. Explain State reads and invalidation, choose a correction, and name evidence that would prove or falsify it.
7. **UI-Q007:** A senior review exposes this failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. Explain State hoisting, choose a correction, and name evidence that would prove or falsify it.
8. **UI-Q008:** A senior review exposes this failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. Explain Immutable collections, choose a correction, and name evidence that would prove or falsify it.
9. **UI-Q009:** A senior review exposes this failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. Explain Stability and skipping, choose a correction, and name evidence that would prove or falsify it.
10. **UI-Q010:** A senior review exposes this failure: List mutable اتغيرت in-place فالواجهة ما اتحدثتش، أو composable تعمل network call كل recomposition. Explain Recomposition evidence, choose a correction, and name evidence that would prove or falsify it.
11. **UI-Q011:** A senior review exposes this failure: LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED. Explain LaunchedEffect keys, choose a correction, and name evidence that would prove or falsify it.
12. **UI-Q012:** A senior review exposes this failure: LaunchedEffect(Unit) تقرأ userId قديمة، أو key متغيرة كل frame تعيد network request، أو collector تستمر بعد view STOPPED. Explain DisposableEffect cleanup, choose a correction, and name evidence that would prove or falsify it.

## Answer key

1. **UI-Q001:** The LayoutManager positions and recycles the visible layout, the Adapter creates and binds ViewHolders, and each ViewHolder holds row views. The adapter’s DiffUtil callback defines logical item identity and visible content equality. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q001.md)
2. **UI-Q002:** The logical item is the same, so areItemsTheSame returns true. The displayed title changed, so areContentsTheSame returns false and the row should be rebound. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q002.md)
3. **UI-Q003:** ListAdapter expects a new list to be submitted for changes; mutating the currently displayed list breaks a useful diff snapshot. I would create a new list with immutable row models, submit it, and test the old/new content policy. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q003.md)
4. **UI-Q004:** The Fragment can outlive its view, so the observer may update or retain an obsolete binding. I would observe view updates with viewLifecycleOwner and clear the binding reference in onDestroyView. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q004.md)
5. **UI-Q005:** I can claim the tested policy distinguishes stable row ID from content and detaches a list container. I cannot claim DiffUtil animations, adapter notifications, Fragment cleanup or accessibility work, because no AndroidX component ran. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q005.md)
6. **UI-Q006:** Compose tracks observable state reads and schedules affected scopes when values change. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q006.md)
7. **UI-Q007:** Hoist state as value plus events to the lowest common owner that needs coordination. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q007.md)
8. **UI-Q008:** Publishing immutable snapshots makes equality and change ownership auditable. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q008.md)
9. **UI-Q009:** Stability can enable skipping, but false stability declarations can hide changes and break UI. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q009.md)
10. **UI-Q010:** Use layout inspector or tracing and measure expensive work; counts alone are not a user problem. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q010.md)
11. **UI-Q011:** Keys define effect identity; a change cancels the old coroutine and starts a new one. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q011.md)
12. **UI-Q012:** Register and unregister the same observer at a lifecycle-aware boundary. [Complete answer](../Interview-Question-Bank/Model-Answers/UI-Q012.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
