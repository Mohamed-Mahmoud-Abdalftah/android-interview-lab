---
id: "MOD-10"
question: "How do navigation contracts work across modules?"
topic: "Gradle Modularization & Dependency Boundaries"
code: "MOD"
group: "B"
phase: 4
priority: "P1"
order: 363
editorial_status: "reviewed"
---

# MOD-10

## Original interview question

How do navigation contracts work across modules?

## What the interviewer evaluates

- Separate destination identity/API from screen implementation.
- Explain app registration, deep links, arguments and versioning.
- Preserve module dependency direction and restoration.

## Concept and technical explanation

In a decoupled multi-module architecture, Feature A cannot instantiate or reference screens in Feature B at compile time because direct dependencies are forbidden. A navigation contract establishes a decoupled communication protocol separating the route destination request from its visual rendering:
- Contract Definition: Feature B's public :api module (or a shared navigation module) defines an abstract navigation interface (e.g., interface ProfileNavigator) or a serializable destination route object (e.g., @Serializable data class ProfileRoute(val userId: String)).
- Contract Implementation: Feature B's private :impl module implements the destination, configuring the Composable screen, ViewModel injection, and argument unpacking.
- Composition Wiring: The root :app module (or a global NavHost coordinator) aggregates navigation graphs using Hilt multibindings (@IntoSet) or Compose navigation destinations, allowing seamless transitions without compile-time coupling.

## Practical walkthrough (English)

Type-safe cross-module navigation using Compose Navigation routes and contract interfaces:
```kotlin
// 1. In :feature:detail:api (Lightweight contract module)
@Serializable
data class DetailRoute(val itemId: String)

interface DetailEntry {
    fun registerGraph(navGraphBuilder: NavGraphBuilder, navController: NavHostController)
}

// 2. In :feature:detail:impl (Renders the Composable screen)
class DetailEntryImpl @Inject constructor() : DetailEntry {
    override fun registerGraph(navGraphBuilder: NavGraphBuilder, navController: NavHostController) {
        navGraphBuilder.composable<DetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<DetailRoute>()
            DetailScreen(itemId = route.itemId, onBack = { navController.popBackStack() })
        }
    }
}

// 3. In :feature:feed:impl (Navigates using only the public route contract)
@Composable
fun FeedItem(item: FeedItem, navController: NavHostController) {
    Button(onClick = { navController.navigate(DetailRoute(item.id)) }) {
        Text("View Details")
    }
}
```

## Explanation in Arabic

كيف تعمل عقود التنقل (Navigation Contracts) عبر موديولات أندرويد المتعددة؟

1. طبيعة المشكلة:
   - في Jetpack Navigation أو Compose Navigation العادي، تقوم بكتابة: `navController.navigate(ProfileRoute(userId))`.
   - في مشروع نمطي، إذا كان كلاس `ProfileRoute` وشاشة `ProfileScreen` موجودين في موديول `:feature:profile`، فإن موديول `:feature:feed` لا يستطيع كتابة هذا السطر لأن `:feature:feed` لا يرى `:feature:profile` في وقت التجميع!

2. الحلول المعمارية لعقود التنقل عبر الموديولات:
   - **الحل الأول: نمط `:api` الموديول (API Route Contracts)**:
     * يتم وضع كلاس المسار (`@Serializable data class ProfileRoute(val id: String)`) داخل موديول خفيف `:feature:profile-api`.
     * يستطيع `:feature:feed` استيراد `ProfileRoute` والتنقل إليه بأمان نوعي كامل (Type-Safe Navigation).
     * موديول `:app` فقط هو من يجمع `:feature:profile-impl` ويربط الشاشة بالمسار داخل `NavHost`.
   - **الحل الثاني: واجهة موجه التنقل المجردة (Navigation Interface Delegate)**:
     * واجهة `interface FeedNavigator { fun navigateToProfile(userId: String) }` يتم حقنها في `FeedViewModel`.
     * يتم تنفيذ الواجهة داخل موديول `:app` واستدعاء `navController.navigate(...)` هناك.

## Practical walkthrough

تطبيق Navigation Contracts في Compose Multi-Module باستخدام الـ API Module:
```kotlin
// 📁 في موديول ':feature:profile-api' (موديول عقود خفيف جداً):
@Serializable
data class ProfileDestination(val userId: String)

// 📁 في موديول ':feature:feed' (يستورد فقط profile-api):
@Composable
fun FeedScreen(onNavigateToProfile: (String) -> Unit) {
    Button(onClick = { onNavigateToProfile("user_42") }) { Text("View Profile") }
}

// 📁 في موديول ':feature:profile-impl' (يحتوي على الشاشة الفعلية):
fun NavGraphBuilder.profileScreen() {
    composable<ProfileDestination> {
        ProfileRoute() // الشاشة الفعلية
    }
}

// 📁 في موديول ':app' (يجمع كل الميزات ويربط مسارات الـ NavHost):
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController, startDestination = FeedDestination) {
        composable<FeedDestination> {
            FeedScreen(onNavigateToProfile = { userId ->
                navController.navigate(ProfileDestination(userId)) // آمن نوعياً 100%!
            })
        }
        profileScreen() // تسجيل شاشة البروفايل من الموديول الفعلي
    }
}
```

## Why it matters and how it works

Navigation is a cross-feature capability but destination implementations should remain encapsulated. A route contract can express stable identifiers and expected arguments, while an app graph or registry contributes actual destination code. The back stack and saved state can restore small arguments after eligible process recreation; the destination reloads data from a repository.

## Worked example

Orders exposes `OrderDetailsDestination(orderId)` as a small contract. A notification or Checkout requests it through an app navigator. The app registers the Orders UI destination, validates the route parameter and resolves authorization in the Orders ViewModel. A deep link into a deleted order renders Not Found instead of crashing.

## Trade-offs and decision criteria

Central graph registration is explicit but can become a large file; feature-owned graph contributions scale but need careful API and dependency arrangement. String routes are flexible but typo-prone; typed route APIs depend on Navigation version. A navigation facade simplifies testing but should not become an opaque global service locator.

## Failure modes

A feature imports another's screen implementation. A route contains a large Parcelable and fails after process death. Deep-link arguments bypass authorization. A dynamic feature route is opened before installation. A rename silently breaks notifications or external links.

## Production perspective

Version and test public routes, deep links, argument parsing, app graph assembly and back-stack restoration. Monitor navigation failures and provide a safe fallback for missing or unauthorized destinations.

## Interview answer — short

Navigation contracts allow screens in one module to open destinations in another without direct compile-time coupling. The destination exposes a public interface contract or type-safe route object in an api module, while its implementation module provides the UI screen. The app module binds the graph together using Hilt multibindings or centralized NavHost registration.

## Interview answer — structured

Cross-module navigation requires navigating between screens whose modules cannot see each other at compile time.
A navigation contract solves this problem by separating the navigation request from the destination's implementation.
The destination feature creates a public api module that exposes either a navigation interface or a type-safe Compose route object.
Feature modules that need to trigger navigation depend strictly on this lightweight api module.
To navigate, the caller simply triggers the contract with required arguments, such as an item identifier.
Inside the destination feature's private implementation module, the Composable destination is registered with the NavGraphBuilder, handling argument extraction and ViewModel setup.
The root app module acts as the central coordinator, collecting navigation destination registrations using Hilt multibindings into a set and attaching them to the root NavHost.
This architecture preserves full type safety and modular isolation.

## Interview answer — deep senior

Designing cross-module navigation in modern Android with Jetpack Compose requires bridging the tension between modular encapsulation and type-safe routing.
Historically, teams relied on URI-based deep links or reflection to open activities across modules, but these approaches lacked compile-time verification, leading to runtime crashes when argument keys changed.
Our modern production architecture leverages Compose Navigation with Kotlin serialization and contract multibindings.
When we build :feature:checkout, we split the feature into :api and :impl subprojects.
The :feature:checkout:api module contains a type-safe route declaration, such as @Serializable data class CheckoutRoute(val cartId: String), alongside an abstract interface NavigationEntry.
Because this contract resides in an independent, leaf-level API module, :feature:cart can import :feature:checkout:api and invoke navController.navigate(CheckoutRoute(cartId)) with total type safety, autocompletion, and zero compile-time awareness of CheckoutScreen or its ViewModels.
Inside :feature:checkout:impl, a concrete NavigationEntry implementation maps CheckoutRoute to its Composable screen, injects the ViewModel, and handles backstack pop actions.
To aggregate all destinations into the root NavHost without hardcoding feature classes in :app, we utilize Hilt multibindings.
Each implementation module contributes its NavigationEntry into a Set<NavigationEntry> via @IntoSet.
The root application iterates over this injected set to build the complete graph dynamically.
This design guarantees compile-time safety, completely prevents horizontal coupling, and scales gracefully across dozens of autonomous engineering squads.

## How to answer in the interview

- **Why:** route can outlive process and feature owner.
- **How:** pass small validated IDs.
- **Trade-off:** light contract versus reload cost.
- **Failure case:** large object arg stale after death.
- **Production solution:** cold-start navigation test.

## Deep-dive talking points

Cover route API, app mapping, typed versus string routes, deep-link security, versioning and dynamic install.

## Follow-up questions

- **Interviewer:** "What is the consequence of passing large objects via Navigation route arguments?"
  **Answer:** "It risks crashing the app with `TransactionTooLargeException` during state saving and couples the two screens to an identical data model."

- **Interviewer:** "Can you navigate between features using Android Deep Links?"
  **Answer:** "Yes. Deep links decouple modules via URI strings (`app://user/{id}`), but sacrifice compile-time type checking compared to serialization contracts."

## Self-check rubric

Define a destination contract, show graph mapping, and cover deep link, restoration and install tests.

## References and reviewed-on date

- [Navigation with Compose](https://developer.android.com/develop/ui/compose/navigation) — routes and arguments.
- [Android modularization patterns](https://developer.android.com/topic/modularization/patterns) — graph composition.

Technically reviewed against primary documentation on 2026-10-13.
