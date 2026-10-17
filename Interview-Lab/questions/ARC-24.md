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

## Concept and technical explanation

Designing cross-feature account and session state without circular dependencies requires applying the Dependency Inversion Principle by hoisting authentication contracts into a dedicated foundational module, such as :core:session or :core:user. In a modularized Gradle architecture, independent feature modules (like :feature:checkout and :feature:profile) must never declare horizontal dependencies on each other. Instead, the shared session module defines the immutable UserSession data model and an authoritative SessionRepository interface exposing a StateFlow<UserSession?>. All feature modules depend downward on this core contract. A centralized network authenticator invalidates the session upon encountering HTTP 401 Unauthorized responses, while the root navigation graph in the :app module observes session state changes to execute global logout routing.

## Practical walkthrough (English)

Structuring cross-feature session state across independent Gradle modules:
```kotlin
// 1. In module ':core:session' (Foundational module with zero feature dependencies)
data class UserSession(val userId: String, val authToken: String, val isPremium: Boolean)

interface SessionRepository {
    val activeSession: StateFlow<UserSession?>
    suspend fun updateSession(session: UserSession)
    suspend fun clearSession()
}

// 2. In module ':feature:checkout' (Depends solely on ':core:session', NOT on ':feature:profile')
class CheckoutViewModel @Inject constructor(
    private val sessionRepository: SessionRepository
) : ViewModel() {
    val isUserPremium: StateFlow<Boolean> = sessionRepository.activeSession
        .map { it?.isPremium == true }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)
}

// 3. In module ':app' (Root orchestration module coordinating global logout)
@Composable
fun RootAppNavigation(sessionRepository: SessionRepository) {
    val session by sessionRepository.activeSession.collectAsStateWithLifecycle()
    if (session == null) {
        AuthNavGraph() // Automatically navigates to Login on session expiration
    } else {
        MainAppNavGraph()
    }
}
```

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

Design cross-feature session state by hoisting it into a lower-level :core:session module that feature modules depend on unidirectionally. Expose an immutable StateFlow<UserSession?> from an authoritative SessionRepository, preventing circular Gradle compilation errors and enabling automatic global logout coordination through the root navigation graph.

## Interview answer — structured

Managing shared session state across modularized Android features without inducing circular Gradle dependencies requires strict unidirectional architecture.
Feature modules such as checkout, account, and chat must never depend horizontally on one another. If feature payment imports feature account while account requires payment status, Gradle compilation halts with a circular dependency failure.
To resolve this, we hoist session models and contracts downward into a dedicated foundational module: :core:session. This core module has zero dependencies on any feature modules. All feature modules declare a unidirectional downward dependency on :core:session.
Within :core:session, a singleton SessionRepository owns the active authentication credentials, exposing an immutable StateFlow of UserSession. Feature ViewModels inject this repository to observe session state or check user permissions reactively.
For global session termination, such as receiving an HTTP 401 Unauthorized response, an OkHttp authenticator in :core:network calls clearSession on the repository. The root navigation host in the top-level :app module observes the session flow; when the session becomes null, it invalidates active feature graphs and immediately routes to the login screen.

## Interview answer — deep senior

Under the hood, managing shared identity across a large-scale multi-module build requires preventing module graph cycles and memory leakage. Circular dependencies in Gradle are fatal compile-time errors because the build graph must form a Directed Acyclic Graph (DAG) to determine task ordering and compilation outputs.
By decoupling session state into an API and Implementation structure—such as :core:session-api containing data classes and repository interfaces, and :core:session-data managing encrypted local storage—we minimize compilation dependencies. Feature modules compile against lightweight API interfaces without recompiling data sources when storage implementations change.
When features need to interact across boundaries—for example, when a successful checkout in :feature:checkout must navigate to order history in :feature:profile—features must not navigate directly between each other. Instead, engineers use navigation event hoisting. The checkout feature exposes an output lambda or sealed navigation event such as onOrderCompleted, which the top-level :app orchestrator intercepts to route to the profile screen.
Staff engineers also safeguard session lifecycle by avoiding insecure process-level global singletons. SessionRepository is backed by EncryptedSharedPreferences or encrypted Room storage and securely managed via Hilt in the SingletonComponent.
When a session terminates, the repository cancels active user coroutines and wipes secure storage, guaranteeing that sensitive tokens and cached personal information never leak into subsequent sessions.

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
