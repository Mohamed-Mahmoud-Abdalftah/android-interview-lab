---
id: "ARC-24"
question: "Design a cross-feature account/session state without creating circular dependencies."
topic: "Clean Architecture, MVVM, MVI & UDF"
code: "ARC"
group: "C"
phase: 2
priority: "P1"
order: 169
editorial_status: "reviewed"
---

# ARC-24

## Original interview question

Design a cross-feature account/session state without creating circular dependencies.

## What the interviewer evaluates

Design shared session ownership without feature-to-feature imports or a process-only singleton.

## Explanation in Arabic

كيف تصمم حالة الحساب/الجلسة المشتركة (Cross-Feature Account/Session State) دون الوقوع في مشكلة التبعيات الدائرية (Circular Dependencies)؟

1. معضلة التبعيات الدائرية في التطبيقات المقسمة لموديولات (Circular Dependencies):
   - ميزة المدفوعات `:feature:payment` تحتاج لمعرفة بيانات الحساب النشط `:feature:account`.
   - وميزة الحساب `:feature:account` تريد معرفة حالة الدفع واشتراك المستخدم من `:feature:payment`.
   - في نظام Gradle، إذا اعتمد موديول A على B واعتمد B على A، يفشل البناء فوراً مع خطأ Circular Dependency!

2. الحل المعماري القياسي: استخراج موديول مشترك في الطبقة الأساسية (Inversion via Core:User / Core:Session):
   - **إنشاء وحدة مخصصة للـ Session في الـ Core Layer**: تسمى `:core:session` أو `:core:user`.
   - هذا الموديول يقع في مستوى أدنى ويعتمد عليه كل من `:feature:payment` و `:feature:account`.
   - يحتوي على:
     * `data class UserSession(val userId: String, val authToken: String, val tier: AccountTier)`.
     * `interface SessionRepository` توفر `val activeSession: StateFlow<UserSession?>`.

3. إدارة أحداث تسجيل الخروج (Global Logout Handling):
   - عند انتهاء الجلسة أو استلام HTTP 401 من أي طلب، يتم استدعاء `sessionRepository.clearSession()` في الـ Core.
   - تستمع شاشة التنقل الرئيسية (Root NavHost) لهذا التدفق، وتقوم بإلغاء كل الشاشات والعودة فورياً لشاشة تسجيل الدخول.

## Practical walkthrough

هيكلة Session State في Core Module مشترك دون أي تبعيات دائرية:
```kotlin
// 1. في module :core:session (موديول أساسي يعتمد عليه الجميع دون حلقات دائرية):
data class UserSession(val userId: String, val token: String, val isPremium: Boolean)

interface SessionRepository {
    val sessionFlow: StateFlow<UserSession?>
    suspend fun updateSession(session: UserSession)
    suspend fun terminateSession()
}

// 2. في module :feature:payment (يعتمد على :core:session فقط):
class PaymentViewModel @Inject constructor(
    private val sessionRepository: SessionRepository
) : ViewModel() {
    fun verifyUserCanPay() {
        val currentSession = sessionRepository.sessionFlow.value
        // التحقق من الجلسة دون أي اعتماد على موديول :feature:account!
    }
}

// 3. في module :app أو Root Navigation (مراقبة الجلسة والتوجيه العام):
@Composable
fun RootAppNav(sessionRepository: SessionRepository) {
    val session by sessionRepository.sessionFlow.collectAsStateWithLifecycle()
    if (session == null) {
        LoginNavGraph() // إذا انتهت الجلسة ننتقل لشاشة تسجيل الدخول تلقائياً
    } else {
        MainAppNavGraph()
    }
}
```

## Why it matters and how it works

Shared state needs one owner and a dependency direction that prevents cycles. A narrow core contract lets features observe session facts while a data implementation owns persistence and refresh. DI composes the graph.

## Worked example

Conceptual module graph: `:core:session-api` defines `SessionState` and `SessionRepository`; `:feature:profile` and `:feature:checkout` depend on that API; `:core:session-data` implements it; `:app` binds implementation. Neither feature imports the other. Token material stays out of `SessionState` exposed to UI.

## Trade-offs and decision criteria

A shared core module adds a dependency hub; keep its API small and stable. An app-level coordinator may suffice for a tiny codebase. Avoid one global mutable object as a shortcut, because tests and process recovery become fragile.

## Failure modes

Checkout reads `ProfileViewModel.currentUser`, creating lifecycle coupling and circular feature dependencies. Or a singleton keeps an in-memory `isLoggedIn` Boolean after token expiry. Use one session owner backed by storage and server validation.

## Production perspective

A multi-feature wallet app exposes `Authenticated(userId)` or `SignedOut` to features; server access checks remain authoritative. Logout invalidates in-flight operations, clears local state, and shows sign-in consistently after recreation.

## Interview answer — short

Design cross-feature session state by hoisting it into a lower-level `:core:session` or `:core:user` module that feature modules depend on unidirectionally. Expose an immutable `StateFlow<UserSession?>` from a singleton `SessionRepository`, preventing circular Gradle dependencies and enabling global reactive logout handling.

## Interview answer — structured

Managing cross-cutting account and session state across features without inducing circular dependencies requires strict architectural layering.

First, **The Core Session Inversion Pattern**. Next, features (`:feature:checkout`, `:feature:settings`, `:feature:chat`) must never depend on each other horizontally.
Instead, we hoist identity and session contracts into a dedicated foundational module: **`:core:session`** (or `:core:model`). `:core:session` has zero feature dependencies. All feature modules depend unidirectionally downward onto `:core:session`.
**Reactive Session Repository**. Inside `:core:session`, a singleton `SessionRepository` manages active authentication credentials, exposing `val activeSession: StateFlow<UserSession?>`.
Feature ViewModels inject `SessionRepository` to inspect user identity or observe permission changes. **Global Session Invalidation (401 Handling)**.
An OkHttp Authenticator in `:core:network` catches HTTP 401 Unauthorized responses. It calls `sessionRepository.clearSession()`. Finally, the top-level `RootNavHost` in the `:app` module observes `activeSession`. When nullified, it tears down active feature graphs and routes immediately to authentication.


## Interview answer — deep senior

Under the hood, in Gradle multi-module builds, circular dependencies (`:feature:A -> :feature:B -> :feature:A`) cause fatal compilation graph cycles. By applying the **Dependency Inversion Principle**, if Feature A needs to trigger an action in Feature B (e.g. Payment completed, navigate to Order History in Account), Feature A must **never import Feature B directly**.

Instead, we use **API/Impl splits** or **Event/Navigation Hoisting**.

First, feature A exposes an output navigation lambda: `onPaymentSuccess: (OrderId) -> Unit`. Finally, the top-level orchestration module (`:app`), which knows both `:feature:payment` and `:feature:account`, wires the navigation call from Payment to Account.

This preserves complete compilation independence: the payment team can build and test `:feature:payment` in total isolation without compiling the account module.


## How to answer in the interview

- **Why:** cross-feature state can create cycles.
- **How:** central contract with one authoritative owner.
- **Trade-off:** shared core versus coupling.
- **Failure case:** stale account response leaks into new session.
- **Production solution:** session generation and authorization checks.

## Deep-dive talking points

Draw module edges, token ownership, refresh/logout races, process-death recovery and server authority.

## Follow-up questions

- **Interviewer:** "What is the role of the `:app` module in feature navigation?"
  **Answer:** "The `:app` module sits at the top of the dependency graph and depends on all feature modules. It wires navigation flows between features, keeping feature modules decoupled from one another."

- **Interviewer:** "How do you handle OkHttp token refresh without circular DI dependencies?"
  **Answer:** "Provide a specialized `TokenProvider` interface in `:core:network` implemented by `:core:session`, or use a custom OkHttp Interceptor/Authenticator injected via Dagger/Hilt."

## Self-check rubric

Sketch an acyclic module graph and explain how checkout reacts to logout after rotation and process death.

## References and reviewed-on date

- [Android modularization guide](https://developer.android.com/topic/modularization) — module dependency design.
- [Android data layer](https://developer.android.com/topic/architecture/data-layer) — repository state ownership.

Technically reviewed against primary documentation on 2026-10-13.
