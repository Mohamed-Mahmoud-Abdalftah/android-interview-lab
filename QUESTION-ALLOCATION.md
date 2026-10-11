# Interview question allocation — final authored state

This file records the question bank that actually exists. `CONTENT-MANIFEST.json` remains the source of truth for paths and review status.

## Complete inventory

| Deliverable | Authored and reviewed |
|---|---:|
| Interview questions | 300 |
| Separate model answers | 300 |
| Debugging scenarios | 50 |
| Coding challenges | 30 |
| Mock interview packs | 8 |

Every question has a separate answer file. Each answer includes a direct spoken response, Egyptian Arabic explanation, mechanics, a common weak answer, answered follow-ups, a polished English answer and a scoring rubric.

## Questions by domain

| Prefix | Domain | Questions |
|---|---|---:|
| `KOT` | Kotlin and JVM foundations | 30 |
| `COR` | Coroutines and Flow | 30 |
| `AND` | Android internals | 30 |
| `ARC` | Architecture and DI | 30 |
| `UI` | Views, Compose and navigation | 30 |
| `PRO` | Production engineering and security | 30 |
| `SYS` | Mobile system design | 30 |
| `INT` | Leadership, behavioral and technical English | 30 |
| `DSA` | DSA and live coding | 10 |
| `POS` | POS and payment hardware | 10 |
| `ART` | ART, DEX, runtime and shrinking | 10 |
| `CON` | Advanced concurrency | 10 |
| `EUI` | Advanced UI engineering | 10 |
| `STF` | Staff-level system design | 10 |
| **Total** | | **300** |

## Questions by difficulty

Difficulty is a practice label, not a learner score.

| Difficulty | Questions |
|---|---:|
| Foundational | 58 |
| Intermediate | 76 |
| Senior | 166 |
| **Total** | **300** |

## Questions by primary interview style

A question can exercise more than one skill, but its front matter records one primary style.

| Style | Questions |
|---|---:|
| Debugging | 71 |
| Architecture | 64 |
| Code review | 63 |
| Conceptual | 40 |
| System design | 26 |
| Product Android | 15 |
| Live coding | 11 |
| Behavioral | 5 |
| Performance | 5 |
| **Total** | **300** |

## Scenario and coding allocation

The 50 scenarios are separate production investigations with symptoms, hypotheses, evidence, correction, regression coverage and rollout or rollback reasoning. The 30 coding challenges contain constraints, edge cases, reference code, tests where executable behavior is claimed and review rubrics.

## Mock interviews

`MOCK-001` through `MOCK-008` are authored. They cover:

1. Kotlin and Coroutines.
2. Android internals.
3. Architecture and data.
4. Views and Compose.
5. Production engineering and security.
6. DSA live coding.
7. Mobile system design and leadership.
8. A full loop with an optional POS branch.

The packs expose questions before their answer keys and publish the evaluation rubric. Timed or scored practice starts only when the learner explicitly chooses Interview Simulation Mode.

## Navigation

- [By topic](Interview-Question-Bank/BY-TOPIC.md)
- [By difficulty](Interview-Question-Bank/BY-DIFFICULTY.md)
- [By interview style](Interview-Question-Bank/BY-INTERVIEW-STYLE.md)
- [Mock interviews](Mock-Interviews/README.md)
