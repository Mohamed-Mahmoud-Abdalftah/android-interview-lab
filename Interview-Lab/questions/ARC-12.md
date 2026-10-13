---
id: "ARC-12"
question: "How should domain/data errors be mapped into actionable UI errors?"
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "B"
phase: 2
priority: "P1"
order: 157
editorial_status: "reviewed"
---

# ARC-12

## Original interview question

How should domain/data errors be mapped into actionable UI errors?

## What the interviewer evaluates

Map typed domain/data failure categories into actionable UI behavior without leaking raw exception text.

## Explanation in Arabic

كيف يتم تحويل أخطاء طبقتي النطاق والبيانات (Domain / Data Errors) إلى أخطاء واجهة مستخدم مفهومة وقابلة للتنفيذ (Actionable UI Errors)؟

1. المشكلة في تسريب استثناءات الطبقات الخارجية (Leaking Raw Exceptions):
   - عرض نصوص مثل `java.net.SocketTimeoutException` أو `HTTP 502 Bad Gateway` للمستخدم هو تجربة مستخدم كارثية وغير مفهومة، وتسريب لمعلومات النظام التقنية.
   - كما أن طبقة الـ UI لا يجب أن تفحص كود أخطاء HTTP (مثل فحص `code == 401`).

2. رحلة تحويل الأخطاء عبر الطبقات الثلاث:
   - **في طبقة الـ Data**: التقاط `HttpException` أو `IOException` وتحويلها إلى **Typed Domain Errors** (مثل `AppError.NetworkTimeout`, `AppError.Unauthorized`).
   - **في طبقة الـ Domain**: اتخاذ قرارات الأعمال (مثل محاولة إعادة الطلب Retry أو توجيه المستخدم لتسجيل الدخول).
   - **في طبقة الـ Presentation**: تحويل الـ Domain Error إلى **Actionable UI Error** يحمل:
     * رسالة مترجمة واضحة (`UiText.StringResource(R.string.network_timeout_msg)`).
     * زر تصحيحي قابل للتنفيذ (Actionable button: مثل زر "إعادة المحاولة Retry" أو "تسجيل الدخول").

3. نمط `UiText` لمنع تسريب الـ Android Context إلى الـ ViewModel:
   - استخدام Sealed Class يسمى `UiText` يمثل إما نصاً ثابتاً (`UiText.DynamicString`) أو معرف مورد (`UiText.StringResource(R.string.xyz)`).
   - يتيح للـ ViewModel تحديد المورد دون الحاجة لـ Context، وتقوم دالة الـ Composable بقراءته عبر `uiText.asString()`.

## Practical walkthrough

نمط UiText وتحويل الأخطاء التقنية إلى أخطاء واجهة قابلة للإصلاح:
```kotlin
// 1. DOMAIN LAYER: تصنيف الأخطاء كـ Domain Errors نقية:
sealed interface DomainError {
    data object NetworkOffline : DomainError
    data object SessionExpired : DomainError
    data class ServerError(val code: Int) : DomainError
}

// 2. PRESENTATION HELPER: تمثيل النصوص المترجمة دون الحاجة لـ Context في ViewModel:
sealed interface UiText {
    data class Dynamic(val value: String) : UiText
    data class Resource(@StringRes val resId: Int, val args: List<Any> = emptyList()) : UiText

    @Composable
    fun asString(): String = when (this) {
        is Dynamic -> value
        is Resource -> stringResource(resId, *args.toTypedArray())
    }
}

// 3. PRESENTATION LAYER: نموذج خطأ تفاعلي قابل للتنفيذ:
data class ActionableUiError(
    val message: UiText,
    val actionLabel: UiText,
    val onAction: () -> Unit
)

// في الـ ViewModel: التحويل من DomainError إلى ActionableUiError:
fun mapError(error: DomainError): ActionableUiError = when (error) {
    is DomainError.NetworkOffline -> ActionableUiError(
        message = UiText.Resource(R.string.error_no_internet),
        actionLabel = UiText.Resource(R.string.retry),
        onAction = { retryLastAction() }
    )
    is DomainError.SessionExpired -> ActionableUiError(
        message = UiText.Resource(R.string.error_session_expired),
        actionLabel = UiText.Resource(R.string.login_again),
        onAction = { navigateToLogin() }
    )
    is DomainError.ServerError -> ActionableUiError(
        message = UiText.Resource(R.string.error_server_generic),
        actionLabel = UiText.Resource(R.string.dismiss),
        onAction = { clearError() }
    )
}
```

## Why it matters and how it works

Error mapping separates transport details from product decisions. Stable categories let UI render guidance and tests assert behavior without parsing strings. Keep diagnostic causes and correlation IDs in protected logs, not public UI text.

## Worked example

Conceptual mapping: repository catches an HTTP 401 and yields `AuthRequired`; transport timeout yields `Uncertain(requestId)` for a submitted payment; ViewModel maps these to `LoginAgain` or `CheckingStatus` screen states. Cancellation propagates rather than becoming `Unknown`.

## Trade-offs and decision criteria

More categories improve actionability but can overfit every HTTP code. Model decisions the UI can actually make. Preserve unknown failures with observability and a safe generic message. Localization belongs in UI/resources.

## Failure modes

A repository catches `Throwable`, including coroutine cancellation, and maps every case to “retry,” causing cancelled requests to trigger UI errors. Rethrow cancellation and classify only expected failures. Raw server messages can leak account details or mislead.

## Production perspective

An account app gives offline users a retry with cached data, unauthorized users a reauthentication route, and validation errors field-level hints. Telemetry records safe category and correlation ID, never a token.

## Interview answer — short

Map technical errors into actionable UI errors through layer boundaries: Data maps raw IO/HTTP exceptions into typed Domain errors (e.g. `NetworkOffline`, `SessionExpired`). The ViewModel maps Domain errors into `ActionableUiError` containing localized `UiText` resource references and executable recovery callbacks (e.g. Retry, Login).

## Interview answer — structured

Transforming raw technical failures into actionable user experiences is a benchmark of enterprise architecture.

1. **Data Layer Translation**: Data sources catch raw platform exceptions (`HttpException`, `SocketTimeoutException`, `SQLiteConstraintException`) and convert them into strongly typed **Domain Errors** (e.g. `DataError.Network.Timeout`, `DataError.Auth.Unauthorized`). Raw stack traces and HTTP status codes must never cross into presentation.

2. **Presentation Layer Mapping**: The ViewModel maps domain errors into a presentation-centric model: the **Actionable UI Error**:
   - **Localized Message**: Encapsulated using a `UiText` wrapper (`UiText.StringResource(R.string.error_no_internet)`), allowing the ViewModel to stay pure and Context-free while supporting instant language changes.
   - **Recovery Action**: Every error must empower the user with an actionable recourse—such as a 'Retry' button, 'Re-authenticate' redirect, or 'Check Settings' link.

This ensures users are never greeted with incomprehensible raw exceptions while decoupling the UI from backend status codes.

## Interview answer — deep senior

The `UiText` pattern is vital for ViewModel testability. If a ViewModel injects Android `Context` or `Resources` merely to call `getString(R.string.error)`, it breaks pure JVM unit test isolation and requires mocking Android framework objects. With `UiText.Resource(R.string.error_id)`, the ViewModel returns a lightweight data class holding the integer resource ID. Unit tests simply assert `assertThat(state.error.message.resId).isEqualTo(R.string.error_id)` in sub-millisecond JVM tests.

In Compose, extracting the string is seamless: composables call `error.message.asString()` which internally invokes `stringResource()`, reacting to configuration changes automatically.

For production telemetry, the raw technical exception is logged to Crashlytics or Datadog in the Data layer before being sanitized, ensuring engineers have stack traces while users receive friendly, actionable prompts.

## How to answer in the interview

- **Why:** error semantics drive safe action.
- **How:** map transport to domain to UI action.
- **Trade-off:** precise types versus modeling cost.
- **Failure case:** timeout shown as decline and user pays again.
- **Production solution:** typed errors and user-safe recovery.

## Deep-dive talking points

Trace an IOException, 401, validation response and uncertain payment timeout through data/domain/UI layers.

## Follow-up questions

- **Interviewer:** "Why shouldn't ViewModels call `context.getString(resId)` directly?"
  **Answer:** "Holding `Context` in ViewModels risks memory leaks and destroys pure JVM unit testability. Using the `UiText` abstraction defers string resolution to the Composable rendering phase."

- **Interviewer:** "What is an 'actionable' error versus a passive error?"
  **Answer:** "A passive error simply displays 'An error occurred'. An actionable error explains what happened and provides a concrete recovery mechanism, such as 'Connection lost. [Retry]' or 'Card expired. [Update Payment]'."

## Self-check rubric

Can you map four failures to different user actions and explain where localization, cancellation and telemetry belong?

## References and reviewed-on date

- [Android UI events](https://developer.android.com/topic/architecture/ui-layer/events) — state-driven UI actions.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — data boundary.

Technically reviewed against primary documentation on 2026-10-13.
