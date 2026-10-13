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

Navigation contracts decouple screen transitions in multi-module apps. Route destinations are placed in lightweight :api modules using Kotlin Serialization types, allowing callers to navigate with full type-safety. The :app module hosts the NavHost, registering destinations and linking screen composables from feature implementation modules.

## Interview answer — structured

In multi-module applications, features cannot reference peer screen classes directly. Navigation contracts solve this by decoupling the destination definition from the screen implementation:

1. **Contract in `:feature:*:api`**: We define the navigation target as a serializable route type (`@Serializable data class UserProfileRoute(val id: String)`) inside a lightweight API module. Any feature needing to navigate to the profile imports only this tiny API contract.

2. **Implementation in `:feature:*:impl`**: The feature implementation module exposes an extension function on `NavGraphBuilder` (e.g. `fun NavGraphBuilder.userProfileScreen(...)`) registering the composable entry.

3. **Assembly in `:app`**: The `:app` module imports both modules and configures the top-level `NavHost`. When feature `A` triggers navigation, it passes the typed contract from `feature-b-api` to the controller. The destination matches without feature `A` ever knowing how the destination screen is implemented or tested.

## Interview answer — deep senior

With modern **Type-Safe Compose Navigation (Navigation 2.8+)**, navigation contracts achieve compile-time safety without raw string URLs.

Under the hood, routes are typed Kotlin classes serialized via `kotlinx.serialization`. However, when architecting navigation contracts across modules, two runtime constraints must be respected:

1. **Serializable Model Independence**: Never include complex domain models inside navigation route arguments (e.g. `data class CheckoutRoute(val cart: CartDomainModel)`). Large objects violate Android's `Bundle` size limits (risking `TransactionTooLargeException`) and violate encapsulation. Route arguments must strictly be lightweight primitives (IDs, keys, or query tokens). The destination screen fetches full data from its own repository.

2. **State Restoration Across Process Death**: Type-safe navigation routes automatically serialize into the `SavedStateHandle`. When Android OS terminates the process in the background and restores it, Compose Navigation deserializes the route arguments flawlessly without manual bundle parsing.

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
