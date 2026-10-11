---
id: "DAT-16"
question: "How should conflicts be resolved when local and server state diverge?"
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "B"
phase: 3
priority: "P1"
order: 273
editorial_status: "reviewed"
---

# DAT-16

## Original interview question

How should conflicts be resolved when local and server state diverge?

## What the interviewer evaluates

Resolve divergent local/server state using versions, domain merge and conflict UX.

## Explanation in Arabic

لما local وserver اختلفوا، ما ينفعش قاعدة واحدة لكل البيانات. نحتفظ بـbase version/ETag مع edit، والسيرفر يعمل compare-and-set أو يرجع conflict. ممكن merge حقول مستقلة، أو server-wins لبيانات authoritative، أو user review للنصوص؛ الأموال والstock لا تتحسم بـlast-write-wins على الموبايل. كل resolution نفسه operation جديدة بهوية واضحة.

## Why it matters and how it works

Conflict detection requires a common base or version vector/ETag; timestamps from device clocks are unreliable as sole authority. A three-way merge compares base, local and remote changes. Preserve both versions until resolution to avoid data loss. Server remains final arbiter for shared invariants.

## Worked example

Conceptual Kotlin conflict model; merge implementation is domain-specific and should not silently discard either side.

```kotlin
data class VersionedNote(val text: String, val version: String)
sealed interface MergeDecision {
    data class Merged(val text: String) : MergeDecision
    data class NeedsUser(val local: String, val remote: String) : MergeDecision
}
fun decide(base: VersionedNote, local: String, remote: VersionedNote): MergeDecision =
    if (remote.version == base.version) MergeDecision.Merged(local)
    else MergeDecision.NeedsUser(local, remote.text)
```

## Trade-offs and decision criteria

Server-wins is simple but can lose offline user work; client-wins can overwrite others. Field-level merge is useful only when fields are independent; CRDTs add complexity and suit specific collaborative domains. User review preserves intent but costs UX.

## Failure modes

Using wall-clock last-write-wins across devices can choose the wrong update due to skew. Retrying stale write without version precondition can erase remote changes. Deleting local pending data on 409 destroys recovery context.

## Production perspective

A notes app stores base/local/remote versions and offers merge review when both edited text. A bank balance never client-merges; it refreshes authoritative server ledger and reconciles pending operations.

## Interview answer — short

“I detect divergence with server versions or ETags, then apply a domain-specific rule: merge independent fields, use server authority for protected data, or ask the user. I preserve the local edit until resolution.”

## Interview answer — structured

“Offline sync needs a conflict contract. Each local edit remembers the server version it was based on. The server conditionally accepts it or returns a conflict with current state. For independent fields I may merge; for a note text changed on both sides I may show a review UI; for money the backend ledger wins. I do not use device timestamps as a sole authority because clocks drift. I keep both versions and a pending operation until a resolution is confirmed. Server-wins is simple but can lose offline user work; client-wins can overwrite others. Field-level merge is useful only when fields are independent; CRDTs add complexity and suit specific collaborative domains. User review preserves intent but costs UX. A notes app stores base/local/remote versions and offers merge review when both edited text.”

## Interview answer — deep senior

“I start by identifying invariants and user intent. A version/ETag allows optimistic concurrency: the server accepts only if the base version still matches. On conflict, a three-way merge can preserve non-overlapping field edits; overlapping text changes may need human choice. Client-wins and server-wins are policies with real data-loss tradeoffs, not defaults. Financial inventory/account state must be resolved by server transactions and operation IDs, never by local timestamp. I persist the unresolved local edit and remote snapshot, expose conflict state, and make the resolution a new idempotent operation. Tests include clock skew, delete-versus-edit, repeated conflict and process death during resolution. Conflict detection requires a common base or version vector/ETag; timestamps from device clocks are unreliable as sole authority. A three-way merge compares base, local and remote changes. Preserve both versions until resolution to avoid data loss. Server remains final arbiter for shared invariants. Using wall-clock last-write-wins across devices can choose the wrong update due to skew. Retrying stale write without version precondition can erase remote changes. Deleting local pending data on 409 destroys recovery context. A notes app stores base/local/remote versions and offers merge review when both edited text. A bank balance never client-merges; it refreshes authoritative server ledger and reconciles pending operations. Server-wins is simple but can lose offline user work; client-wins can overwrite others.”

## Deep-dive talking points

Trace base/local/remote values, domain invariants and conflict persistence.

## Follow-up questions

- [DAT-15](../dat-15/): What data must outbox hold? **Answer:** stable ID, payload and base version for conflict detection.
- [DAT-07](../dat-07/): Who owns truth? **Answer:** local DB for displayed snapshot, server for shared authoritative data.

## Self-check rubric

Can I detect conflict, choose policy by domain, preserve user edit and test skew/deletion?

## References and reviewed-on date

- [Android offline-first guidance](https://developer.android.com/topic/architecture/data-layer/offline-first) — conflict resolution.

Technically reviewed by automated technical/editorial inspection against the linked primary documentation on 2026-10-11; no human review or Android device test is claimed. The example is illustrative unless explicitly stated otherwise.
