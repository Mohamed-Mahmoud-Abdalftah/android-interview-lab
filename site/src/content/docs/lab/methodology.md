---
title: Methodology and privacy
description: Source fidelity, editorial status, local progress, and limitations
---

The canonical Interview Lab questions come verbatim from `Senior_Android_Interview_Master_Bank.md`: 485 IDs in 21 topics. The earlier academy lessons and 300 Q&A pairs retain their separate IDs and are not counted as completed answers for the new bank.

Each canonical page shows its editorial status. **Source-only** means the question is preserved for practice but has no complete, technically reviewed answer. A **reviewed** label requires a distinct Arabic explanation, mechanics, worked example or justified omission, trade-offs, failures, production context, English answers, rubric, relevant references, and technical review.

Bookmarks, notes, progress, due dates, and session summaries stay in browser `localStorage`. There is no account, tracking service, or audio upload. Export saves JSON to your device; import replaces local progress only after confirmation. Clearing browser data removes progress unless you exported it. The earlier academy has a separate local progress store.

On supported secure origins, a small service worker caches pages and assets after they are visited. It requests the network first when online and can serve previously visited pages offline. It does not pre-download the full bank, and unvisited pages are unavailable offline.

Android APIs and security advice change. Verify version-sensitive claims against official Android, Kotlin, Gradle, and OWASP documentation before production use. Interview practice does not certify hiring readiness or payment security.
