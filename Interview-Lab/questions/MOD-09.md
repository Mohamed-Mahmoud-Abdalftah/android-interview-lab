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

Feature modules communicate without direct coupling through three patterns: shared reactive state in lower data/domain layers, API contract modules (:feature:x-api) exposing abstract interfaces, and decoupled navigation using URL deep links or navigation delegates wired centrally in the :app module.

## Interview answer — structured

Enforcing zero direct compile-time coupling between peer feature modules requires three complementary architectural patterns:

1. **Shared Reactive Data Layer**: When features need to exchange information (e.g. adding an item in `:feature:catalog` that updates a badge in `:feature:cart`), they never communicate ViewModel-to-ViewModel. Instead, both depend downward on `:data:cart`. The catalog ViewModel mutates the repository, and the cart badge reacts to the resulting `StateFlow` emitted by the single source of truth.

2. **API/Implementation Module Splitting**: When feature `A` must explicitly invoke a capability in feature `B`, split feature `B` into `:feature:b:api` (containing interfaces and models) and `:feature:b:impl`. Feature `A` depends only on `:api`. The concrete implementation is bound via Hilt in `:app`.

3. **Decoupled Navigation**: Navigation between features is delegated to type-safe route contracts, deep link URIs, or navigation interfaces implemented in `:app`. Feature `A` requests navigation to an abstract route without importing Feature `B`'s Composable or Activity.

## Interview answer — deep senior

A frequent anti-pattern when communicating between features is **Global In-Memory Event Buses** (e.g. broadcasting untyped JSON strings or arbitrary event classes across an application-wide SharedFlow).

Event buses create invisible, untraceable data dependencies: if an event payload changes, nothing fails at compile time, leading to silent runtime bugs. Furthermore, event buses fail across Android process recreation—if the app process dies while an event was fired, the listener in another screen will never receive it.

By channeling inter-feature communication through **durable domain repositories backed by Room or DataStore**, data persistence and reactive UI synchronization are guaranteed across process death, background updates, and screen lifecycles.

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
