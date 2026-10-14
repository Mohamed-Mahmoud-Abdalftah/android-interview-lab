---
id: "ARC-09"
question: "How does UI state differ from business/domain state?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "A"
phase: 2
priority: "P1"
order: 154
editorial_status: "reviewed"
---

# ARC-09

## Original interview question

How does UI state differ from business/domain state?

## What the interviewer evaluates

Separate durable business facts from screen-specific rendering and interaction state.

## Explanation in Arabic

كيف تختلف حالة الواجهة (UI State) عن حالة الأعمال/النطاق (Business / Domain State)؟

1. ما هي حالة الأعمال (Business / Domain State)؟
   - تمثل الحقيقة الأساسية للبيانات والمنتج (Source of Truth) بصرف النظر عن كيفية أو مكان عرضها.
   - أمثلة: رصيد الحساب البنكي، عناصر سلة التسوق الفعلية في قاعدة البيانات، وحالة اشتراك المستخدم (Active / Expired).
   - تتميز بأنها: طويلة الأجل (Long-lived)، مستقلة عن أجهزة العرض وشاشات الهواتف، ولا تتغير بمجرد تفاعل بصري.

2. ما هي حالة الواجهة (UI State)؟
   - تمثل ما يراه المستخدم ويتفاعل معه على الشاشة في اللحظة الراهنة.
   - أمثلة: هل مؤشر التحميل (Spinner) ظاهر؟ ما هو نص رسالة الخطأ المترجمة المعروضة؟ أي تبويب محدد حالياً؟ هل القائمة منسدلة (Expanded)؟ وما هو النص المكتوب في حقل البحث؟
   - تتميز بأنها: مؤقتة (Ephemeral)، تعيش مع الشاشة، وتتأثر بالحجم والدوران ونوع الجهاز.

3. لماذا يُعتبر الخلط بينهما خطأ معمارياً فادحاً؟
   - إذا قمت بحفظ متغير مثل `isDropdownExpanded: Boolean` داخل الـ Domain Entity، فإنك لوثت بيانات البزنس بتفاصيل واجهة مستخدم مؤقتة لا معنى لها في قاعدة البيانات أو على السيرفر!

## Practical walkthrough

توضيح الفرق العملي بين Domain State و UI State وكيف يحول الـ ViewModel بينهما:
```kotlin
// 1. DOMAIN STATE (حالة البزنس النقية - تعيش في Domain/Database):
data class BankAccount(
    val accountNumber: String,
    val balanceCents: Long,
    val currency: String,
    val isOverdrawn: Boolean
)

// 2. UI STATE (حالة العرض المخصصة للشاشة - تعيش في Presentation):
@Immutable
data class AccountDetailsUiState(
    val isLoading: Boolean = false,
    val formattedBalance: String = "", // مجهزة للعرض المباشر: "-$150.00"
    val balanceColor: Color = Color.Black, // أحمر إذا كان مكشوفاً
    val isDepositButtonEnabled: Boolean = true,
    val errorMessage: String? = null
)

// 3. التحويل في الـ ViewModel:
fun BankAccount.toUiState(): AccountDetailsUiState {
    return AccountDetailsUiState(
        isLoading = false,
        formattedBalance = CurrencyFormatter.format(balanceCents, currency),
        balanceColor = if (isOverdrawn) Color.Red else Color.Green,
        isDepositButtonEnabled = !isOverdrawn
    )
}
```

## Why it matters and how it works

UI state describes what to display now, while domain state describes application facts and rules. A ViewModel transforms domain/data streams into screen state; the repository remains responsible for the underlying source of truth.

## Worked example

Conceptual mapping: `Order(status = Pending, totalMinor = 1299)` is domain data; `CheckoutUiState(showSpinner = true, totalText = "EGP 12.99", canRetry = false)` is presentation. On server confirmation, repository updates order status; ViewModel emits a new UI state. The label is not persisted as canonical money.

## Trade-offs and decision criteria

A separate UI model costs mapping but prevents display details from contaminating domain. Very small screens may render a domain model directly if no distinct presentation contract exists. Do not persist every transient UI flag as though it were business truth.

## Failure modes

A ViewModel sets `isPaid = true` after an HTTP timeout because it saw a local click. The client has no confirmed outcome; render pending verification and reconcile. Another failure is storing locale-formatted amount in database and later parsing it for payment logic.

## Production perspective

An order details screen observes Room-backed order status and composes locale-specific text. After process death, it reloads business status from repository; selected accordion state may restore from saved UI state if worthwhile.

## Interview answer — short

Business/domain state represents persistent, presentation-independent business facts (e.g. account balance, cart items in DB). UI state represents transient, presentation-specific rendering requirements (e.g. loading spinners, active tab indexes, formatted strings, and error banners).

## Interview answer — structured

Distinguishing between UI state and Business/Domain state is a cornerstone of clean separation of concerns.

First, **Business / Domain State**. Next, represents core domain truth and invariants independently of how or whether data is displayed.
Examples: A user's remaining credit balance, an authentication token, or an order's fulfillment status. Maintained in data/domain layers, often backed by local databases (Room) or remote servers. It survives Activity destructions and app process restarts.
**UI State (Presentation State)**. Represents the visual rendering of the screen at a specific instant.
Examples: Whether a loading indicator is spinning, active text field inputs, whether an accordion item is expanded, or localized error strings. Finally, scoped to the UI lifecycle (ViewModel or Composable) and ephemeral in nature.

The ViewModel acts as the transformer: it observes long-lived domain state, applies presentation logic, and projects it into formatted, immutable `UiState` snapshots.


## Interview answer — deep senior

A frequent architectural defect is leaking UI state down into domain repositories or databases. For example, adding `var isSelected: Boolean` or `var isExpanded: Boolean` directly onto a database entity or domain model corrupts pure business definitions with transient UI concerns. If that entity is reused across a notification service, widget, or background sync worker, those UI properties are completely meaningless and cause data corruption bugs.

Conversely, storing domain business rules inside UI state creates duplicate logic across screens. For instance, checking if an account is eligible for a loan must be evaluated in a domain Use Case, not computed ad-hoc within a composable's `UiState` mapping lambda.

In testing, domain state is tested via assertions on repository updates, whereas UI state is tested by asserting that domain events produce expected visual states in `StateFlow`.


## How to answer in the interview

- **Why:** UI rendering and business authority differ.
- **How:** derive UiState from durable domain state.
- **Trade-off:** responsive UI versus extra mapping.
- **Failure case:** saveable success badge outlives truth.
- **Production solution:** reconcile backend and render current state.

## Deep-dive talking points

Contrast durable order status with a screen spinner, selected tab, and localized total. Discuss process death and server authority for payments.

## Follow-up questions

- **Interviewer:** "Can UI state exist without domain state?"
  **Answer:** "Yes. Purely transient UI states—like an accordion expansion toggle, a dialog visibility flag, or animation progress—are UI states that have zero backing domain state."

- **Interviewer:** "Where should the formatting of a date timestamp (Long to String) occur?"
  **Answer:** "In the Presentation layer (ViewModel or Presentation Mapper). Formatting depends on device locale and UI display rules, which have no place in the pure domain layer."

## Self-check rubric

Give two domain facts and two UI-only fields, then explain how a ViewModel derives UI state after recreation.

## References and reviewed-on date

- [Android state holders](https://developer.android.com/topic/architecture/ui-layer/stateholders) — screen UI state versus data.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — application data ownership.

Technically reviewed against primary documentation on 2026-10-13.
