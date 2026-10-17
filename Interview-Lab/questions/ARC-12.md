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

## Concept and technical explanation

Domain and data layer errors represent technical, transport, or business invariant failures (such as SocketTimeoutException, HTTP 401/403/500, SQLiteConstraintException, or DomainValidationException). The UI layer must never consume or display raw exceptions directly, as doing so leaks infrastructure details, displays unlocalized cryptic messages to users, and causes main-thread crashes when uncaught exceptions bubble up. Instead, robust architectures apply an error transformation pipeline: the Data layer intercepts raw throwables and categorizes them into typed, domain-safe failure models. The Presentation layer (ViewModel) maps these domain errors into user-actionable UI error representations containing localized string resource identifiers, error severities, and explicit recovery actions (such as retry lambdas, re-authentication triggers, or navigation intents).

## Practical walkthrough (English)

Transforming low-level exceptions into user-actionable UI models:
```kotlin
// 1. DOMAIN LAYER: Typed, framework-agnostic error hierarchy
sealed interface DomainError {
    object NetworkUnavailable : DomainError
    object Unauthorized : DomainError
    data class ServerError(val code: Int) : DomainError
    data class BusinessRuleViolated(val reason: String) : DomainError
}

// 2. PRESENTATION LAYER: Actionable UI error model with string resources
data class ActionableUiError(
    @StringRes val titleRes: Int,
    @StringRes val messageRes: Int,
    @StringRes val actionLabelRes: Int?,
    val recoveryAction: (() -> Unit)?
)

fun DomainError.toUiError(onRetry: () -> Unit, onReAuth: () -> Unit): ActionableUiError = when (this) {
    is DomainError.NetworkUnavailable -> ActionableUiError(
        titleRes = R.string.error_no_internet_title,
        messageRes = R.string.error_no_internet_desc,
        actionLabelRes = R.string.action_retry,
        recoveryAction = onRetry
    )
    is DomainError.Unauthorized -> ActionableUiError(
        titleRes = R.string.error_session_expired_title,
        messageRes = R.string.error_session_expired_desc,
        actionLabelRes = R.string.action_login_again,
        recoveryAction = onReAuth
    )
    else -> ActionableUiError(R.string.error_generic_title, R.string.error_generic_desc, null, null)
}
```

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

Catch raw low-level exceptions in the data layer, translate them into typed domain errors, and map them in the ViewModel into actionable UI models. UI errors should provide localized string resources and clear recovery actions, such as retry callbacks or re-authentication triggers, rather than raw exception messages.

## Interview answer — structured

Converting technical exceptions into actionable UI errors is essential for building resilient, user-friendly Android applications.

Raw network exceptions like SocketTimeoutException or HTTP 500 status codes must never leak into the presentation layer. The repository intercepts infrastructure failures and maps them into a typed domain failure hierarchy, such as NetworkUnavailable or SessionExpired.

In production, the ViewModel translates these domain failures into UI-facing models. Rather than exposing raw strings that violate localization, it binds Android string resource IDs alongside explicit recovery actions, such as triggering a retry lambda or launching an account recovery intent.
As for user experience, this mapping ensures the UI presents empathetic, actionable guidance. The interface informs users exactly what went wrong and how to fix it, whether that means enabling airplane mode, checking card limits, or tapping a retry button.


## Interview answer — deep senior

Under the hood, robust error architecture follows an anti-corruption pipeline that prevents infrastructure crashes while preserving actionable diagnostic context. When an HTTP client throws a 401 Unauthorized or a database write violates a foreign key constraint, the Data layer catches the throwable and categorizes it into a sealed domain error type. By wrapping operations in a custom domain Result, the system eliminates uncaught runtime exceptions on coroutine dispatchers.
Inside the Presentation layer, the ViewModel maps the domain error into a presentation state model. A major pitfall in legacy applications is passing raw exception messages like java.net.UnknownHostException directly into UI TextViews, which exposes internal implementation details and fails multi-language localization.
Senior engineers model actionable errors as structured data classes: data class UserMessage containing message resource IDs, action labels, and action types. This decouples the Composable from error decisions; Compose simply renders the text resource and invokes the callback when the user taps the action button.
Furthermore, staff engineers distinguish between transient errors—which are presented via Snackbars or dialogs without clearing screen content—and terminal errors, which replace the entire screen with a full-page empty error layout. In production telemetry, raw error details and correlation trace IDs are simultaneously dispatched to crash reporting services like Datadog or Crashlytics while the user receives a graceful, localized recovery experience.

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
