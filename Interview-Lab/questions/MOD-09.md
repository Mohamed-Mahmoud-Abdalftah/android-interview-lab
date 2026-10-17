---
id: "MOD-09"
question: "How should feature modules communicate without direct coupling?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 362
editorial_status: "reviewed"
---

# MOD-09

## Original interview question

How should feature modules communicate without direct coupling?

## What the interviewer evaluates

- Select contracts, navigation events or shared state by actual relationship.
- Keep ownership and dependency direction explicit.
- Address result delivery and asynchronous consistency.

## Concept and technical explanation

Direct dependencies between sibling feature modules violate horizontal architectural layering, generate circular dependency traps, and severely impair incremental build performance. To communicate without direct coupling, feature modules must employ decoupled interaction patterns:
1. API/Impl Separation Pattern: A feature is split into an exposed public :api module containing navigation contracts, interfaces, and minimal public models, and a private :impl module holding UI, ViewModels, and implementations. Feature A depends strictly on :feature:b:api.
2. Abstract Navigation Interfaces: Feature A declares an abstract navigation contract (e.g., CheckoutLauncher) that Feature B's implementation fulfills, wired together at the root :app level via Hilt dependency injection.
3. Deep Link Event Routing: Screens are launched via URI contracts (e.g., myapp://checkout?id=123) resolved dynamically by Android's navigation component or intent filters.
4. Reactive Domain Event Buses: Features communicate state updates asynchronously by emitting and observing shared Kotlin Flow events hosted in core domain contracts.

## Practical walkthrough (English)

Cross-feature communication via API contract interfaces and Hilt multibindings:
```kotlin
// 1. In :feature:checkout:api (Lightweight contract, no UI or ViewModels)
interface CheckoutNavigationContract {
    fun launchCheckout(context: Context, cartId: String)
}

// 2. In :feature:cart:impl (Needs to open checkout without importing its internals)
class CartViewModel @Inject constructor(
    private val checkoutNav: CheckoutNavigationContract
) : ViewModel() {
    fun onCheckoutClicked(context: Context, cartId: String) {
        checkoutNav.launchCheckout(context, cartId)
    }
}

// 3. In :feature:checkout:impl (Implements the contract)
class CheckoutNavigationImpl @Inject constructor() : CheckoutNavigationContract {
    override fun launchCheckout(context: Context, cartId: String) {
        context.startActivity(Intent(context, CheckoutActivity::class.java).putExtra("id", cartId))
    }
}

// 4. In :app (Wires interface to implementation via Hilt module)
@Module
@InstallIn(SingletonComponent::class)
abstract class NavigationWiringModule {
    @Binds abstract fun bindCheckoutNav(impl: CheckoutNavigationImpl): CheckoutNavigationContract
}
```

## Explanation in Arabic

كيف تتواصل موديولات الميزات (Feature Modules) مع بعضها البعض دون وجود اقتران مباشر (Direct Coupling) بينها؟

1. التحدي الأساسي:
   - في بنية الـ Multi-Module النظيفة، موديول `:feature:feed` لا يستطيع استيراد أي كلاس من `:feature:profile` أو `:feature:cart` (لا توجد تبعية `implementation(projects.feature.cart)`).
   - ومع ذلك، يحتاج المستخدم في شاشة الـ Feed إلى الضغط على صورة الناشر لفتح ملفه الشخصي في شاشة الـ Profile، أو الضغط على زر إضافة إلى السلة.

2. الأنماط المعمارية الثلاثة للتواصل غير المقترن:
   - **نمط الـ API/Impl (Contract Extraction)**: لكل ميزة موديولان: `:feature:cart-api` و `:feature:cart-impl`. موديول `:feature:feed` يعتمد فقط على `:feature:cart-api` الذي يحتوي على واجهات مجردة ومسارات بدون أي كود UI.
   - **التنقل عبر Deep Links أو مسارات مجردة (Navigation Routes)**: فتح الشاشات عبر مسار نصي أو نوعي (`NavigationContract` أو URIs مثل `app://profile/{userId}`) يتولى موديول الـ `:app` ربطه بالشاشة الفعلية.
   - **التواصل عبر حالة مشتركة في الـ Data Layer (Shared State via Repositories)**: إذا أضاف المستخدم عنصراً إلى السلة من شاشة الـ Feed، لا تتحدث الـ Feed مباشرة مع الـ Cart Screen؛ بل تقوم باستدعاء `CartRepository.addToCart(id)`. تقوم شاشة الـ Cart بمراقبة `CartRepository.cartFlow` وتحديث واجهتها تلقائياً عبر تدفق البيانات التفاعلي (Reactive Single Source of Truth).

## Practical walkthrough

التواصل بين موديولين عبر Shared State Repository وعقد التنقل المجرد:
```kotlin
// 1. التواصل لحفظ وتحديث البيانات: عبر طبقة الـ Data المشتركة وليس بين الـ ViewModels:
// في :feature:catalog:
@HiltViewModel
class CatalogViewModel @Inject constructor(
    private val cartRepository: CartRepository // واجهة من :domain:cart
) : ViewModel() {
    fun addItemToCart(item: Product) {
        viewModelScope.launch { cartRepository.addItem(item.id) }
        // لا نكلم شاشة الـ Cart مباشرة! مجرد كتابة في الـ Single Source of Truth
    }
}

// 2. التواصل للتنقل (Navigation Decoupling) عبر عقد مجرد:
// في :feature:profile-api (موديول عقد خفيف جداً):
interface ProfileNavigationContract {
    fun openUserProfile(context: Context, userId: String)
}

// في :feature:feed:
class FeedNavigator @Inject constructor(
    private val profileNav: ProfileNavigationContract // محقونة من الخارج!
) {
    fun onAvatarClicked(context: Context, authorId: String) {
        profileNav.openUserProfile(context, authorId)
    }
}
// موديول الـ Feed لا يعلم أي شيء عن كلاسات شاشة الـ Profile أو تطبيقها الفعلي!
```

## Why it matters and how it works

Direct feature implementation imports create cycles and couple release cadence. A stable API or app-level coordinator converts the relationship into a directed edge. Navigation can pass small identifiers and results through back-stack/saved-state mechanisms where appropriate. Shared domain data belongs in a repository rather than two screens copying mutable objects.

## Worked example

Catalog opens checkout with a product ID. Checkout loads authoritative price and stock through `ProductRepository` contract; app navigation maps `CheckoutDestination(productId)` to the checkout implementation. On completion, checkout returns an order ID or updates the orders repository. Catalog does not call checkout's ViewModel or inspect its Composables.

## Trade-offs and decision criteria

An interface module adds API work but decouples real consumers. App orchestration is explicit but may enlarge top-level wiring. A shared event bus is flexible yet hides ownership and can lose or duplicate events. Direct coupling can be acceptable inside one cohesive feature module; do not split solely to then reconstruct it with adapters.

## Failure modes

Features import each other's DTOs and create a cycle. A global SharedFlow drops a checkout result while no screen collects. A shared singleton holds stale selected product after account switch. Navigation passes an entire mutable cart that cannot restore after process death.

## Production perspective

Document contracts, event ownership and replay/acknowledgment policy. Test deep links, background/foreground transitions and process recreation across feature boundaries. Enforce dependency edges in CI.

## Interview answer — short

Feature modules must never depend directly on sibling feature modules. They communicate through decoupled patterns: splitting features into public api contracts and private implementations; invoking abstract navigation interfaces wired by the app module via Hilt; routing destinations through deep link URIs; or observing reactive shared event flows managed in core domain contracts.

## Interview answer — structured

Direct coupling between feature modules is an architectural anti-pattern that creates circular dependencies and degrades build times.
To allow features to interact safely, we rely on decoupled architectural patterns.
The primary approach is the API and Implementation pattern.
Each feature is divided into a lightweight public api module that exposes only interfaces and contract models, and a private implementation module containing UI screens, ViewModels, and business logic.
When Feature A needs to interact with Feature B, it declares an implementation dependency strictly on Feature B's api module, keeping Feature B's implementation details encapsulated.
For navigation, Feature A invokes an abstract navigator interface.
The concrete implementation of that navigator is supplied by Feature B and wired together by the root app module using Hilt dependency injection.
For broadcast notifications, features emit domain events onto shared Kotlin Flow streams, allowing completely decoupled state updates across the app.

## Interview answer — deep senior

In enterprise multi-module Android systems, horizontal feature-to-feature dependencies are strictly forbidden by architectural policy.
When :feature:cart imports :feature:checkout directly, any refactoring inside checkout's UI or ViewModel triggers a full recompilation of cart, invalidating the build cache and risking circular loops.
Our primary architectural solution is the API/Impl structural pattern.
Every vertical feature is bifurcated into two discrete Gradle subprojects: :feature:name:api and :feature:name:impl.
The :api module contains solely pure Kotlin interfaces, navigation routes, and immutable parcelable arguments.
It has zero dependencies on Android UI frameworks or sibling features, allowing it to compile in a fraction of a second.
When the cart feature needs to initiate checkout, it imports solely :feature:checkout:api.
The concrete implementation in :feature:checkout:impl is hidden behind Kotlin's internal visibility modifier.
The root app module acts as the mediator: it imports both :impl modules and uses Hilt to bind the interface to its concrete implementation.
At runtime, CartViewModel receives the navigator instance via constructor injection and executes navigation seamlessly.
For asynchronous state synchronization, such as clearing a shopping cart upon successful logout, we use reactive domain event streams.
An authentication feature emits a UserLoggedOutEvent onto a shared SharedFlow hosted in a core domain contract module, and independent feature repositories observe the stream without knowing which component initiated the event.

## How to answer in the interview

- **Why:** feature internals should remain independent.
- **How:** communicate by stable IDs/contracts.
- **Trade-off:** decoupling versus extra routing.
- **Failure case:** shared mutable singleton leaks state.
- **Production solution:** integration test app composition.

## Deep-dive talking points

Discuss data contracts, app orchestration, navigation IDs, result delivery, repository source of truth and cycle checks.

## Follow-up questions

- **Interviewer:** "Why shouldn't one ViewModel inject another ViewModel directly?"
  **Answer:** "ViewModels are tied to specific lifecycle owners (Activity/Fragment/NavBackStackEntry). Cross-injecting ViewModels leads to severe lifecycle leaks and crashes."

- **Interviewer:** "How does Deep Link navigation benefit multi-module apps?"
  **Answer:** "It provides uniform navigation that works identically for in-app screen transitions, push notifications, and external web URLs without compile-time module coupling."

## Self-check rubric

Specify a data contract, navigation contract, result semantics and integration test.

## References and reviewed-on date

- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — feature boundaries.
- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — navigation arguments.

Technically reviewed against primary documentation on 2026-10-13.
