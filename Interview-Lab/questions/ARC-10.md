---
id: "ARC-10"
question: "What is Single Source of Truth (SSOT)?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 155
editorial_status: "reviewed"
---

# ARC-10

## Original interview question

What is Single Source of Truth (SSOT)?

## What the interviewer evaluates

Define one authoritative owner per data type and distinguish local cache from server authority.

## Explanation in Arabic

SSOT يعني لكل نوع data في التطبيق مصدر authoritative واضح، والتحديثات تمرّ عليه بدل كل شاشة تمسك copy mutable وتتنافس. في offline-first app، Room ممكن تكون local source of truth اللي UI تراقبه، والnetwork refresh يكتب فيها. لكن لمدفوعات أو account balance السيرفر يفضل authority النهائي حتى لو DB هي مصدر العرض المحلي. “واحد” مش معناها server واحد لكل شيء؛ بعض UI element state محلي للشاشة. المهم تعرف مين يحسم التعارض وكيف تتعامل مع stale/offline data.

## Practical walkthrough

SSOT معناها مكان authoritative لكل معلومة، مش “استخدم Room دائمًا”. Offline notes قد تكون Room هي مصدر UI مع sync backend؛ payment status authority عند backend والـRoom local projection. حدد write path وconflict policy، وخلي UI تراقب stream واحدة بدل cache منفصلة في ViewModel. اختبر اختلاف local/remote ولا تمسح pending edits عند refresh.

## Why it matters and how it works

A single source of truth prevents conflicting copies and creates a predictable update path. Android offline-first guidance often uses a local data source as the observable app source, with network synchronization feeding it. Server-authoritative business facts still require reconciliation.

## Worked example

Conceptual flow: `Room.observeOrders()` feeds the repository Flow and UI; `refreshOrders()` fetches remote records and writes them transactionally to Room; UI never renders the raw Retrofit response directly. For an uncertain payment, repository requests server status before promoting local `Pending` to `Paid`.

## Trade-offs and decision criteria

A local SSOT improves offline UX and consistent observation but adds synchronization and stale-data policy. Direct network rendering is simpler for a tiny online-only screen but makes cache and recreation behavior less coherent. Choose per data type.

## Failure modes

A screen renders fresh network data while another observes an older Room row, so users see contradictory order status. Route successful refresh through the same source and version/conflict rules. Never treat a local cache as authority for authorization.

## Production perspective

An offline news app uses Room as SSOT for articles and tracks `lastSyncedAt`; a wallet app may use Room as display cache but always confirms transfers on the server. Telemetry distinguishes stale data from refresh errors.

## Interview answer — short

SSOT means one clearly owned authoritative source for each kind of app data. In offline-first Android, UI often observes a local database that network sync updates; server authority still governs business facts like payments.

## Interview answer — structured

I identify where a value becomes official for the app and make all consumers read through that path. For an offline-first feed, the repository can expose Room as the observable source and write network refreshes into it. That prevents one screen from showing a raw response while another shows stale cached data. I still separate local display truth from server authority: a payment cache cannot authorize a transfer. I define stale-data and conflict behavior rather than assuming “single source” solves synchronization automatically. For a news feed, I might let Room be the local observable source, with network refresh writing into it. For a payment, I can display locally cached status but must reconcile it with server authority before declaring completion. Each data type needs an explicit owner.

## Interview answer — deep senior

SSOT is an ownership rule, not a claim that one database answers every question. A screen’s selected tab can be locally owned; product data may be database-backed; a transfer status may need server confirmation. The repository should state what consumers observe, how network updates are applied, and how conflicts or stale data are signaled. In an offline-first app I commonly expose a Flow from Room and update Room transactionally after refresh, so all screens converge on one local source. After process death the same persisted source restores state. For server-authoritative decisions I do not promote optimistic client flags to facts; I reconcile with the backend and retain pending uncertainty. I test refresh races, stale cache, offline behavior, and conflict resolution. I would specify conflict policy and freshness, not just draw a database icon. What happens when two refreshes overlap, the device is offline for a week, or a write is rejected by the server? The repository should expose stale metadata or a refresh error while keeping useful cached data. A single source of truth means consumers converge through a defined path; it does not mean local values are universally authoritative. Tests should cover races, process death, and contradictory updates.

## How to answer in the interview

- **Why:** conflicting copies create stale UI.
- **How:** name authority and derive projections.
- **Trade-off:** offline responsiveness versus reconciliation.
- **Failure case:** two mutable caches disagree.
- **Production solution:** single observable path with conflict policy.

## Deep-dive talking points

Draw Room-backed observation plus network refresh. Specify stale data, conflict, atomic writes, and server-authoritative payment reconciliation.

## Follow-up questions

- [ARC-19](../arc-19/): How are server updates applied? **Answer:** through repository sync into the chosen local source with conflict rules.
- [ARC-09](../arc-09/): Is a UI flag an SSOT for payment? **Answer:** no; it is presentation state, not authority.

## Self-check rubric

Identify a source of truth for an offline feed and for payment confirmation; describe one conflicting-copy failure and recovery path.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository and source-of-truth responsibilities.
- [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) — local source of truth.

Technically reviewed against the linked official Android architecture guidance on 2026-10-11. Conceptual flows and snippets are not device-tested.
