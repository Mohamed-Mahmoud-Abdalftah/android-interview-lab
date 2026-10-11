---
id: MOCK-007
status: reviewed
---
# MOCK-007 — System design and leadership

**Recommended time:** 75 minutes. **Default:** Learning Mode; scoring is optional and self-reported. Read the rubric before starting.

## Question-only interview

1. **SYS-Q006:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain BFS and DFS choice, choose a correction, and name evidence that would prove or falsify it.
2. **SYS-Q007:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain Heap invariant, choose a correction, and name evidence that would prove or falsify it.
3. **SYS-Q008:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain Dijkstra precondition, choose a correction, and name evidence that would prove or falsify it.
4. **SYS-Q009:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain Dynamic-programming state, choose a correction, and name evidence that would prove or falsify it.
5. **SYS-Q010:** A senior review exposes this failure: Dijkstra على negative edge، BFS على weighted graph، أو DP table من غير تعريف معنى الخانة. Explain Graph test boundaries, choose a correction, and name evidence that would prove or falsify it.
6. **SYS-Q011:** A senior review exposes this failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. Explain Session state machine, choose a correction, and name evidence that would prove or falsify it.
7. **SYS-Q012:** A senior review exposes this failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. Explain Refresh race, choose a correction, and name evidence that would prove or falsify it.
8. **SYS-Q013:** A senior review exposes this failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. Explain Secure storage, choose a correction, and name evidence that would prove or falsify it.
9. **SYS-Q014:** A senior review exposes this failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. Explain Account partitioning, choose a correction, and name evidence that would prove or falsify it.
10. **SYS-Q015:** A senior review exposes this failure: refresh قديمة ترجع بعد logout فتحيي session، أو cache من account A تظهر في B. Explain Server authority, choose a correction, and name evidence that would prove or falsify it.
11. **SYS-Q016:** A senior review exposes this failure: network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync. Explain Source of truth, choose a correction, and name evidence that would prove or falsify it.
12. **SYS-Q017:** A senior review exposes this failure: network response قديمة تكتب فوق local edit، أو delete يختفي ويرجع بعد sync. Explain Durable outbox, choose a correction, and name evidence that would prove or falsify it.

## Answer key

1. **SYS-Q006:** BFS gives shortest edge count in an unweighted graph; DFS fits reachability and recursive structure with depth risks. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q006.md)
2. **SYS-Q007:** The root is the priority optimum; arbitrary iteration is not globally sorted. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q007.md)
3. **SYS-Q008:** Weights must be non-negative and stale heap entries need handling. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q008.md)
4. **SYS-Q009:** Define exactly what dp state means, recurrence, base cases, and evaluation order. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q009.md)
5. **SYS-Q010:** Cover cycles, self-loops, disconnected nodes, duplicate edges, overflow, and invalid weights. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q010.md)
6. **SYS-Q011:** Model signed out, authenticating, active, refreshing, and reauthentication-required with explicit transitions. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q011.md)
7. **SYS-Q012:** A refresh result is accepted only for the current account generation and cannot revive a logged-out session. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q012.md)
8. **SYS-Q013:** Keystore protects key material; it does not make arbitrary stored plaintext or server trust unnecessary. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q013.md)
9. **SYS-Q014:** Database rows, caches, work, and notifications must carry account identity and clear or switch atomically. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q014.md)
10. **SYS-Q015:** The backend validates authorization and revocation; client checks improve UX but are not final security. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q015.md)
11. **SYS-Q016:** UI observes local canonical state while sync updates it through transactions. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q016.md)
12. **SYS-Q017:** Persist mutation and local state atomically so process death cannot lose intent. [Complete answer](../Interview-Question-Bank/Model-Answers/SYS-Q017.md)

## Published rubric

Score each answer 0–4: **0** absent/unsafe, **1** definition only, **2** correct core contract, **3** mechanism plus failure/test, **4** senior trade-off, evidence boundary, and clear communication. Coding questions also require compiling logic, boundary tests, and honest complexity. The score is practice evidence, never a hiring guarantee.

## Debrief

Record three items: the first wrong assumption, the slowest explanation, and the missing test. Return to linked lessons before repeating this pack. Do not memorize the answer key wording.
