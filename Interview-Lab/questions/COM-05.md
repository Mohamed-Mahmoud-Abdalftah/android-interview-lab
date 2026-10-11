---
id: "COM-05"
question: "Compare remember, rememberSaveable, and ViewModel state."
topic: "Jetpack Compose"
code: "COM"
group: "A"
phase: 3
priority: "P1"
order: 234
editorial_status: "reviewed"
---

# COM-05

## Original interview question

Compare remember, rememberSaveable, and ViewModel state.

## What the interviewer evaluates

- Map each state holder to its lifetime and owner.
- Explain process-death restoration without claiming a ViewModel survives it.
- Keep saved bundles small and reload heavy data.

## Explanation in Arabic

`remember` يحتفظ بقيمة أثناء وجود نفس composition، لكنه لا يحميها من Activity recreation. `rememberSaveable` يستخدم saved instance state للأنواع القابلة للحفظ، فيناسب text أو selected tab صغيرة عبر rotation وإعادة إنشاء process عندما يوفر النظام state restoration. ViewModel يملك screen/business state ويبقى عادة عبر configuration change، لكنه يتكون من جديد بعد process death؛ `SavedStateHandle` يحتفظ بحد أدنى من keys/IDs لإعادة تحميل البيانات. لا تخزن response كبير أو token حساس في Bundle.

## Why it matters and how it works

Compose remembers values by composition position and keys. Saveable state uses a registry and Bundle-compatible saving path rather than durable database persistence. A ViewModel has an owner lifecycle independent of individual composable invocations, making it suitable for screen decisions and asynchronous work. After system process death the ViewModel instance is recreated; only saved identifiers or durable storage can restore its meaningful state.

## Worked example

A search screen keeps an expanded-filter chip locally with `rememberSaveable`, while a ViewModel owns the query and result loading because query changes drive repository work. It stores the query or a route ID in `SavedStateHandle` and reloads results after recreation. A temporary animation flag can use `remember` if losing it on recreation is harmless.

## Trade-offs and decision criteria

Local state reduces architectural plumbing; ViewModel state improves sharing and business-rule testing. Saveable values carry serialization/size costs and are not a database. A ViewModel survives rotation but needs explicit recovery for process death. Choose by ownership first, then restoration semantics.

## Failure modes

Remembered form text disappears at rotation. A ViewModel is assumed immortal and shows an empty screen after process death. A huge object is placed in saved state and risks transaction-size errors. Two copies of query state diverge between UI and ViewModel.

## Production perspective

Classify each field as ephemeral UI, restorable UI, or business state; document its owner and reload source. Exercise rotation and system recreation, including missing/stale IDs, rather than relying on a happy-path preview.

## Interview answer — short

“`remember` lasts within composition, `rememberSaveable` restores small UI state through saved state, and a ViewModel owns screen logic across configuration changes but needs saved or durable data after process death.”

## Interview answer — structured

“I decide from ownership and lifetime. A disposable animation flag can live in `remember`; a small user-entered UI value can use `rememberSaveable` so recreation restores it. State that drives repository calls belongs in a ViewModel, which survives ordinary rotation but is rebuilt if the process dies. I save a small identifier with `SavedStateHandle` and reload the heavy data. I avoid duplicating the same query in both the composable and ViewModel.”

## Interview answer — deep senior

“These APIs solve different lifetime problems. `remember` retains a value as long as that keyed composition location remains; it does not imply restoration after the Activity is recreated. `rememberSaveable` participates in Android saved-state restoration for supported small values, so it suits things like an expanded section or draft text when that UI owns them. A ViewModel has the screen owner lifecycle and is appropriate when the value coordinates multiple composables or business operations. It survives configuration changes, but not system process death as an instance. To recover, I keep minimal route or query information in `SavedStateHandle` and reconstruct data from a repository or database. I do not serialize a large response or sensitive secret into a Bundle. For a search page I make one query owner; the UI sends edits, the ViewModel updates query and results, and restoration reloads if necessary. I test rotation, process recreation, and a stale identifier separately because they exercise different failure paths. The choice should follow who needs the state and what loss is acceptable, not a rule that everything must be in ViewModel.”

## Deep-dive talking points

Compare composition lifetime, saved-state registry, ViewModel ownership, process death, and Bundle size.

## Follow-up questions

- Does a ViewModel instance survive system process death? **Answer:** no; save small recovery input and rebuild from durable sources.
- Should a 2 MB API response go in `rememberSaveable`? **Answer:** no; store an ID or query and reload data.
- When is `remember` enough? **Answer:** for local values whose loss when leaving composition or recreation is acceptable.

## Self-check rubric

Assign three example values to owners, explain rotation and process death, and avoid a duplicate source of truth.

## References and reviewed-on date

- [Save UI state in Compose](https://developer.android.com/develop/ui/compose/state-saving) — lifetime and small saved values.
- [Where to hoist state](https://developer.android.com/develop/ui/compose/state-hoisting) — owner choice.

Technically reviewed against these primary sources on 2026-10-11 by automated editorial review. Restoration depends on Android saved-state conditions.
Compare remember, rememberSaveable, and ViewModel state.
