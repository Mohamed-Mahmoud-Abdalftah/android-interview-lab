---
id: SCN-017
lesson_id: KOT-005
status: reviewed
code_verification: not_run
---
# SCN-017 — Erased cache value crashes far from its boundary

**Hypothetical investigation.** A shared cache stores values by string and exposes `fun <T> get(key): T?`. A refactor reuses a key for another model; a screen later crashes with `ClassCastException`.

<p dir="rtl" lang="ar">اجمع write/read call sites، key، runtime class، stack trace، app version وتسلسل rollout. الـgeneric return كانت promise من غير runtime evidence؛ cast اتأخرت لحد الاستخدام فالمكان اللي وقع مش بالضرورة مكان الخطأ. افحص كمان nested collections لأن outer List ممكن تعدي والelement تفشل بعدين.</p>

## Repair and rollout

1. Replace raw string keys with typed keys or a serializer-backed descriptor.
2. Validate untyped values on insertion and treat incompatible old entries as an explicit cache miss.
3. Version persisted keys and migrate or invalidate disposable cache entries deliberately.
4. Add tests for key reuse, malformed values, nested elements and Java/null boundaries.

<p dir="rtl" lang="ar">لو البيانات user-owned مش disposable cache، ما تمسحهاش صامت. اعمل migration بعقد واضح. حط telemetry لنوع key/version والفشل من غير payload. الـunchecked cast، لو ضرورية، تبقى جوه abstraction واحدة بعد validation بدل ما تتكرر في كل screen.</p>

## Senior follow-ups

1. **Would reified get<T>() fix the design?** It can validate a direct runtime class, but it still needs key identity and richer metadata for nested generic values.
2. **Why did the stack trace mislead the team?** Erasure let the invalid promise travel until a concrete use inserted a cast.
3. **What is a safe rollback?** Restore compatible readers while keeping versioned keys; do not reinterpret persisted values under the old untyped contract.

[LAB-016](../Coding-Challenges/LAB-016-runtime-type-registry.md) contains the typed boundary model.
