---
id: "ARC-19"
question: "How do you handle cache and server updates within the data layer?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 164
editorial_status: "reviewed"
---

# ARC-19

## Original interview question

How do you handle cache and server updates within the data layer?

## What the interviewer evaluates

Design cache/server synchronization with a source of truth, stale policy, conflict rules and errors.

## Explanation in Arabic

Data layer تقرر مين المصدر اللي UI تراقبه. في offline-first app، Room غالبًا local SSOT: repository تعرض Flow من DAO، والnetwork refresh يكتب في Room transaction؛ UI ما تعرضش raw response بشكل منفصل. لازم تعرف freshness، invalidation، conflict resolution، وretry. لو server عنده authority زي balance، cache للعرض فقط وما تعتبرش optimistic local change نهائي. كمان تعامل مع concurrent refreshes عشان response قديم ما يكتبش فوق أحدث data؛ استخدم version/timestamp policy موثوقة أو serialize updates.

## Why it matters and how it works

A repository coordinates local and remote sources and gives consumers one observation contract. Offline-first guidance favors a local source of truth. Sync must define write order, staleness, conflict handling and failure behavior.

## Worked example

Conceptual flow: `observeProducts()` reads Room Flow; `refreshProducts()` fetches API pages and writes validated entities in a Room transaction. UI sees the database stream. A failed refresh leaves cached products visible with an error/freshness indicator.

## Trade-offs and decision criteria

Local-first design improves offline UX but adds storage, migration and sync complexity. A simple online-only screen may fetch directly through a repository without a database. Choose based on offline requirements and data authority.

## Failure modes

Two refreshes race: older response arrives last and overwrites newer status. Compare server versions or serialize writes; do not trust client wall-clock alone. Another failure is clearing cache before refresh succeeds, leaving an empty screen offline.

## Production perspective

A delivery app stores route tasks in Room for offline display and queues permitted edits with IDs; server reconciliation resolves conflicts. Sensitive server-authoritative status is confirmed before showing final completion.

## Interview answer — short

The repository coordinates cache and server. In an offline-first app, UI observes a local source of truth while refresh writes into it. I define freshness, conflicts and failure behavior, and keep server authority for sensitive facts.

## Interview answer — structured

I expose one observable data path, often Room Flow, and make refresh update that source rather than letting UI mix raw network and cached records. The repository maps DTOs, writes transactionally, and reports refresh status separately so cached content survives an outage. I define stale-data policy and conflict resolution, especially when refreshes overlap. For payments or balances the local database is a display cache; the server decides the final business status. I would choose a local database as the observable source for an offline feed, then write remote updates into it. If a refresh fails, cached items remain and the UI sees a stale/error indicator. For server-authoritative payment state, the cache is only a display projection.

## Interview answer — deep senior

The design begins with data authority and offline requirements. If a local database is the app’s observable SSOT, all UI reads go through it and remote updates are validated and committed atomically. The repository owns invalidation, freshness metadata, retries and conflict policy. I test a late older response, partial page failure, offline restart, and process death during sync. Simply writing the last response to arrive can regress state, so I use server versions or ordered reconciliation where available. I keep useful cached content on refresh failure and signal staleness to UI. For sensitive facts, such as account balance, server authority remains explicit even when Room is the local render source. The goal is consistent observation, not an illusion of always-fresh data. The hard cases are ordering and conflict. An old response can arrive after a newer one; device wall-clock timestamps can be unreliable; queued edits can be rejected by the server. I define version or sequence rules with the backend where possible, serialize writes when needed, and test partial failures transactionally. A refresh should not clear the cache before replacement succeeds. The repository should expose enough metadata for UI to communicate freshness without forcing every screen to understand network mechanics.

## Deep-dive talking points

Walk cache miss, successful refresh, stale data and racing refresh responses; define authority for payment status.

## Follow-up questions

- [ARC-10](../arc-10/): What is the UI’s local source of truth? **Answer:** often Room in an offline-first design, updated through repository sync.
- [ARC-11](../arc-11/): What happens on failed refresh? **Answer:** preserve cached content and expose refresh error/staleness.

## Self-check rubric

Describe one observable path, one conflict rule and the UI behavior after network failure with cached data.

## References and reviewed-on date

- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth and sync.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository role.

Technically reviewed against the linked official Android guidance on 2026-10-11. Conceptual examples are not device-tested.
