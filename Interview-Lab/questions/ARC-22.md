---
id: "ARC-22"
question: "A Repository returns an API DTO directly to Compose. What coupling risks follow?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 167
editorial_status: "reviewed"
---

# ARC-22

## Original interview question

A Repository returns an API DTO directly to Compose. What coupling risks follow?

## What the interviewer evaluates

Identify transport-schema coupling, null/error leakage and UI churn from direct DTO exposure.

## Explanation in Arabic

عندما يقوم الـ Repository بإرجاع كائن API DTO مباشرة إلى Jetpack Compose: ما هي مخاطر الارتباط (Coupling Risks) المترتبة على ذلك؟

1. تسريب تفاصيل الشبكة والسيرفر إلى طبقة العرض (Infrastructure Leaks):
   - الـ DTO مصمم ليطابق بنية JSON القادمة من السيرفر.
   - إذا اعتمد الـ Composable على `UserDto` مباشرة:
     * أي تغيير بسيط في الـ API من قبل فريق الـ Backend (مثل تغيير اسم حقل، تحويل حقل إلى Array، أو حذفه) سيكسر ملفات الـ UI والـ Compose Layouts فوراً!

2. تدهور أداء وسلاسة Jetpack Compose (Performance & Stability Degradation):
   - كائنات الـ DTO غالباً ما تحوي حقولاً غير مستقرة، أو حقول Nullable متعددة تتطلب فحوصات `if (dto.data != null)` متكررة داخل الـ Composable.
   - كما تضطر دالة الـ Composable لحساب وتنسيق النصوص والتواريخ في كل فريم (Jank Risk) بدلاً من استقبال نصوص جاهزة محسوبة مسبقاً.

3. استحالة عمل Offline Caching ومصادر بيانات متعددة:
   - الـ DTO يمثل استجابة HTTP فقط. إذا أردت جلب البيانات من Room أو Bluetooth، فلن تتوافق الكائنات، مما يدمر فكرة الـ Single Source of Truth.

## Practical walkthrough

تصحيح تسريب الـ DTO وفصل النماذج عبر طبقة وسيطة:
```kotlin
// ❌ كارثة ارتباط: Composable يعتمد مباشرة على Retrofit DTO:
@Composable
fun BadUserBadge(userDto: UserNetworkDto) { // تسريب كائن الشبكة للـ UI!
    // فحص nulls مستمر وتنسيق تواريخ مكلف داخل الـ Composable:
    val formattedDate = SimpleDateFormat("yyyy-MM-dd").format(Date(userDto.timestamp ?: 0L))
    Text("${userDto.first_name} ${userDto.last_name} - $formattedDate")
}

// ✅ كود سليم: فصل تام بنماذج UI نقية ومستقرة:
@Immutable
data class UserBadgeUiModel(
    val fullName: String,
    val formattedJoinedDate: String
)

@Composable
fun GoodUserBadge(user: UserBadgeUiModel) {
    // عرض نقي وفوري بدون أي null checks أو حسابات ثقيلة:
    Text("${user.fullName} - ${user.formattedJoinedDate}")
}
```

## Why it matters and how it works

A repository should hide data sources and expose stable app data. A DTO is optimized for transport, not rendering. Mapping prevents server schema changes from rippling into UI and gives one place for validation and error classification.

## Worked example

Scenario: `ProductDto(priceCents: Long?, title: String?)` is rendered directly. A server rollout changes price unit or omits title; Compose now decides fallback and may display `0`. Instead data maps to `Product(id, Money(minor, currency), title)` or typed invalid-payload error; ViewModel formats locale text.

## Trade-offs and decision criteria

Mapping costs code and allocations. If an internal API is truly stable and the DTO already matches domain semantics, sharing may be acceptable temporarily; document the coupling and test contract changes. High-risk money and auth data deserve explicit models.

## Failure modes

A nullable DTO price gets `?: 0`, turning malformed data into a free product display. Another failure is Compose importing Retrofit annotation types, making a network client replacement require UI edits.

## Production perspective

An ecommerce app maps versioned price payloads and validates currency in data. Compose sees stable `ProductUiState`; API contract tests catch new fields and units before release.

## Interview answer — short

Returning API DTOs directly to Compose tightly couples the UI to backend API schema changes, causes stability issues and recomposition jank from unformatted data and nullable fields, eliminates offline database caching, and prevents isolated UI testing.

## Interview answer — structured

Allowing API DTOs to cross the repository boundary into Jetpack Compose is a severe architectural smell with immediate stability and maintenance risks.

1. **Backend Volatility Spilling into UI**: DTOs are volatile models dictated by server API schemas. If the backend team refactors a field (e.g. from `userName` to `user_handle` or wraps an object in an envelope), that network modification immediately breaks Composable layout files and UI tests across the app.

2. **Compose Performance & Stability Degradation**: DTO classes are not optimized for Compose smart skipping. They often contain mutable properties, standard collections (`List<T>`), or unvalidated nullables, forcing composables to become unskippable and re-render unnecessarily.

3. **In-Composition Formatting Overhead**: When using raw DTOs, composable functions are forced to format currency, parse ISO dates, and concatenate strings inside the composition pass, creating memory churn and dropped frames during 120fps scrolling.

4. **Destruction of Offline-First Architecture**: An API DTO represents HTTP traffic. It cannot unify data with Room database entities or in-memory caches, sabotaging Single Source of Truth architecture.

## Interview answer — deep senior

Under the hood, DTOs prioritize **deserialization ergonomics** (e.g. `@SerialName`, `@JsonClass`, nullable default fallbacks). In contrast, Compose UI models prioritize **rendering efficiency and immutability** (e.g. `@Immutable`, pre-calculated `AnnotatedString`s, localized string resources).

The repository's explicit contractual duty is to map raw DTOs into Domain Entities. The ViewModel then maps Domain Entities into specialized, immutable `UiModel`s. This insulation allows the backend schema to undergo major revisions while the Composable UI remains 100% stable, untouched, and fully functional.

## How to answer in the interview

- **Why:** wire contracts change independently from UI.
- **How:** map and validate before rendering.
- **Trade-off:** boundary code versus direct simplicity.
- **Failure case:** new backend enum crashes/silently succeeds.
- **Production solution:** contract test and explicit unknown handling.

## Deep-dive talking points

Analyze DTO field rename, nullability, units, unknown enum, UI formatting and repository contract tests.

## Follow-up questions

- **Interviewer:** "What happens to Compose skipping when a DTO class is modified?"
  **Answer:** "DTO classes from network libraries typically lack Compose stability annotations, making composables that accept them unskippable and forcing full recompositions on parent invalidations."

- **Interviewer:** "Where should the transformation from DTO to UI model take place?"
  **Answer:** "DTO to Domain model occurs in the Data layer (Repository). Domain model to UI model occurs in the Presentation layer (ViewModel or Presentation Mapper)."

## Self-check rubric

List three coupling risks and sketch the DTO-to-domain-to-UI mapping for a nullable price.

## References and reviewed-on date

- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository abstraction.
- [Android UI layer](https://developer.android.com/topic/architecture/ui-layer) — UI state production.

Technically reviewed against primary documentation on 2026-10-13.
