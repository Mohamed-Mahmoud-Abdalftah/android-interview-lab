---
id: AND-002
title: Configuration change and process death
module: 03-Android-Internals
tier: Core
estimated_minutes: 65
prerequisite_ids: [AND-001]
learning_outcomes:
  - Diagnose a concrete Android runtime failure from evidence
  - Explain the platform contract in Egyptian Arabic and spoken English
  - Review unsafe code and defend a bounded correction
  - Design JVM and Android tests without overstating evidence
status: reviewed
code_verification: tested
last_source_checked: 2026-10-11
source_urls:
  - https://developer.android.com/topic/libraries/architecture/saving-states
  - https://developer.android.com/guide/topics/resources/runtime-changes
  - https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate
example_paths:
  - ../projects/kotlin-jvm-labs/src/main/kotlin/academy/CompletionModels.kt
  - ../projects/kotlin-jvm-labs/src/test/kotlin/academy/CompletionModelsTest.kt
question_ids: [AND-Q006, AND-Q007, AND-Q008, AND-Q009, AND-Q010]
---

# AND-002 — Configuration change and process death

## إحنا بنحل مشكلة إيه؟ — Interview problem

<p dir="rtl" lang="ar">المستخدم كتب draft، لف الشاشة ففضل موجود، لكن بعد ما النظام قتل process رجع لقى الشاشة فاضية. نجاح rotation test خلّى الفريق يفتكر إن state آمنة، مع إن ViewModel كانت بس مخبية المشكلة.</p>

## المفهوم من الصفر — Mental model

<p dir="rtl" lang="ar">Configuration change بتنشئ UI owner جديدة جوه نفس process غالبًا، وViewModel ممكن تحتفظ بالـscreen state. Process death تمسح heap كلها؛ الرجوع يبدأ من saved state صغيرة أو storage durable. صنّف كل state: UI element مؤقت، screen state قابلة لإعادة البناء، ولا business data لازم تتخزن.</p>

## بيشتغل إزاي من جوه؟ — Mechanism

<p dir="rtl" lang="ar">قبل recreation خزّن أقل keys لازمة لإعادة البناء. عند الرجوع اقرأ saved arguments وSavedStateHandle، وبعدها حمّل البيانات الكبيرة من repository. متحطش object graph أو bitmap في Bundle؛ الحجم محدود والنسخة ممكن تبقى stale.</p>

## Trace خطوة بخطوة — Execution trace

<table dir="rtl" lang="ar"><thead><tr><th>الخطوة</th><th>القرار والدليل</th></tr></thead><tbody><tr><td>1</td><td>المستخدم كتب draft، لف الشاشة ففضل موجود، لكن بعد ما النظام قتل process رجع لقى الشاشة فاضية. نجاح rotation test خلّى الفريق يفتكر إن state آمنة، مع إن ViewModel كانت بس مخبية المشكلة.</td></tr>
<tr><td>2</td><td>Configuration change بتنشئ UI owner جديدة جوه نفس process غالبًا، وViewModel ممكن تحتفظ بالـscreen state. Process death تمسح heap كلها؛ الرجوع يبدأ من saved state صغيرة أو storage durable. صنّف كل state: UI element مؤقت، screen state قابلة لإعادة البناء، ولا business data لازم تتخزن.</td></tr>
<tr><td>3</td><td>قبل recreation خزّن أقل keys لازمة لإعادة البناء. عند الرجوع اقرأ saved arguments وSavedStateHandle، وبعدها حمّل البيانات الكبيرة من repository. متحطش object graph أو bitmap في Bundle؛ الحجم محدود والنسخة ممكن تبقى stale.</td></tr>
<tr><td>4</td><td>خزّن navigation identity وinput صغير في saved state، وخزّن business data في database. أعد اشتقاق القيم المحسوبة بدل تكرارها. اختبر recreation وprocess recreation كمسارين مختلفين.</td></tr></tbody></table>

## كود غلط، ليه غلط، وتصحيحه — Wrong and corrected implementation

```kotlin
class EditorViewModel : ViewModel() {
    var draft: String = "" // survives rotation only while process lives
}
```

<p dir="rtl" lang="ar">الكود الغلط بيخلط platform contract مع افتراض محلي، ومفيهوش ownership أو failure policy واضحة. النتيجة ممكن تنجح في happy path وتفشل بعد recreation أو input خارجية أو ضغط production.</p>

```kotlin
fun restoreEditor(saved: Map<String, String>, durableDraft: String?) =
    RestoredEditor(
        draft = saved["draft"] ?: durableDraft.orEmpty(),
        selectedTab = saved["tab"]?.toIntOrNull()?.coerceAtLeast(0) ?: 0,
    )
```

## مثال Production حقيقي وبدائل

<p dir="rtl" lang="ar">خزّن navigation identity وinput صغير في saved state، وخزّن business data في database. أعد اشتقاق القيم المحسوبة بدل تكرارها. اختبر recreation وprocess recreation كمسارين مختلفين. قبل rollout حدد metric صحة، وجرّب failure وrecreation، وخلي logging بأقل بيانات ومن غير secrets. اختار أبسط boundary تحقق العقد؛ ما تزودش component أو thread أو persistence من غير سبب.</p>

## Tests and failure cases

- Pure JVM test للعقد أو reducer لما يكون مستقل عن Android.
- Android recreation/lifecycle test لما النتيجة تعتمد على framework owner.
- Negative inputs عند كل exported أو restored boundary.
- Process death, account switch, cancellation, duplicate delivery, and stale completion where relevant.
- Release evidence names the device/API/build and never upgrades a JVM model into device proof.

## Interview explanation

<p dir="rtl" lang="ar"><strong>إجابة مختصرة:</strong> Configuration change بتنشئ UI owner جديدة جوه نفس process غالبًا، وViewModel ممكن تحتفظ بالـscreen state. Process death تمسح heap كلها؛ الرجوع يبدأ من saved state صغيرة أو storage durable. صنّف كل state: UI element مؤقت، screen state قابلة لإعادة البناء، ولا business data لازم تتخزن.</p>

**English, 20 seconds:** “ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data.”

**English, 60–90 seconds:** “ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data. In production I start from the owning component and the platform boundary, then trace recreation, external input, cancellation, and late delivery. I keep small restoration or command data separate from durable business state, validate untrusted boundaries, and choose evidence that can distinguish the competing causes. I test pure policy on the JVM and use an Android integration or device trace for framework behavior.”

## Senior follow-ups

1. **A ViewModel preserves a form after rotation. Why does that prove nothing about process death?** ViewModel survives a configuration-created owner replacement, but it lives in process memory. Process death removes it; restoration needs saved-state keys and durable data.
2. **Review code that puts a full API response in a Bundle to survive recreation.** A Bundle is a bounded handoff, not a database. Store identity and lightweight input, then reload canonical data from the source of truth.
3. **The UI renders defaults, then saved state, then database data and visibly jumps. Design the restoration order.** Build one state reducer with explicit restoring/loading/content phases. Seed identity from saved state, read local data, and only publish states that the UI can represent honestly.

## Hands-on lab, misconceptions and revision

<p dir="rtl" lang="ar">جاوب الأسئلة من AND-Q006 إلى AND-Q010 بصوتك قبل فتح الإجابة. الاعتقاد إن happy path أو rotation واحدة تثبت Android lifecycle غلط؛ افصل كل owner وentry point وfailure. راجع المصادر الرسمية المتحققة بتاريخ 2026-10-11.</p>

حل [LAB-023](../Coding-Challenges/LAB-023-configuration-change-versus-process-death.md) ثم راجع الاختبارات.


حلّل [SCN-024](../Real-World-Scenarios/SCN-024-draft.md) من غير ما تقرأ الإصلاح الأول.

**Evidence limit:** Official Android behavior is sourced, but this host has no Android SDK/emulator. Pure policy code is marked separately from device evidence.
