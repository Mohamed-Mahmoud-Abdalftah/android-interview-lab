---
id: PRO-Q010-ANSWER
question_id: PRO-Q010
status: reviewed
---
# PRO-Q010 — Complete model answer

<p dir="rtl" lang="ar">migration failure ترتبط غالبًا بـstart/target محددين وSQL أو schema validation ويمكن إعادة إنتاجها من exported file. corruption تظهر integrity/page أو malformed database errors وقد لا ترتبط بمسار إصدار واحد. lock contention تحتاج traces وtransaction durations وbusy/timeout pattern. DataStore read failure تتقسم I/O، corruption وprogrammer exception حسب النوع والpolicy. أستخدم typed error categories، app/schema version، timing وحالة storage، وأعيد الإنتاج بأقل fixture ممكن من غير جمع بيانات مستخدم.</p>

**Spoken answer:** “I classify failures before recovery. Version-specific open errors point to migration logic, integrity failures point toward corruption, and timing plus transaction traces reveal contention. DataStore I/O and corruption follow separate policies. Tests reproduce each boundary, while telemetry records versions, duration, and typed outcomes without user content.”

**Common wrong answer:** Catch every storage exception and return an empty database or default preferences.

**Follow-up 1:** Why is returning empty data dangerous? It converts a diagnosable failure into silent data loss and can trigger destructive remote synchronization.

**Follow-up 2:** What does a graph unit test miss? It misses SQL execution, file integrity, Room schema validation, real locks, disk failures, and Android process behavior.

**Rubric:** Separate failure classes, map each to evidence, reject silent reset, preserve privacy, and state test limitations.
