---
id: "DAT-05"
question: "Compare Room, DataStore, and SharedPreferences."
topic: "Networking, Room, DataStore & Offline-First"
code: "DAT"
group: "A"
phase: 3
priority: "P1"
order: 262
editorial_status: "reviewed"
---

# DAT-05

## Original interview question

Compare Room, DataStore, and SharedPreferences.

## What the interviewer evaluates

Choose structured relational storage versus small preferences, including migration and atomicity.

## Explanation in Arabic

`Room` فوق SQLite للبيانات المنظمة والعلاقات والqueries/transactions وFlow observation. `DataStore` مناسب preferences أو typed small settings بشكل asynchronous وtransactional updates؛ مش قاعدة relational كبيرة. `SharedPreferences` API قديمة synchronous access ممكن تعمل jank وتحتاج حذر في التزامن؛ للـnew settings غالبًا DataStore أفضل. ولا واحد منهم secret vault تلقائيًا.

## Why it matters and how it works

Room verifies SQL at compile time and supports migrations; DataStore serializes preference updates and exposes Flow; SharedPreferences may be used for legacy compatibility/migration. Choose from schema, volume, query and consistency needs. Sensitive values require a separate threat model and appropriate protection.

## Worked example

Conceptual Android DataStore/Room split; names are application types and settings store setup is omitted deliberately.

```kotlin
interface SettingsRepository {
    val darkMode: kotlinx.coroutines.flow.Flow<Boolean>
    suspend fun setDarkMode(enabled: Boolean)
}
interface ArticleDao {
    fun observeArticles(): kotlinx.coroutines.flow.Flow<List<Article>>
    suspend fun upsert(article: Article)
}
// Settings uses DataStore; Article rows use Room.
```

## Practical walkthrough

لو عندك orders/items بعلاقات وqueries وtransaction، Room فوق SQLite مناسبة؛ Entity/DAO ومigrations جزء من contract. Theme أو onboarding flag صغيرة ممكن تتحفظ في Preferences DataStore، وtyped config في Proto/typed DataStore حسب schema. DataStore بتدي Flow وupdate transactionally لكن مش relational DB ولا partial row updates. SharedPreferences موجودة في legacy apps، لكن كثرة synchronous reads/writes ومشاكل consistency تخلي migration لـDataStore منطقيًا حسب الحاجة؛ لا تنقل order table لها. راجع backup/restore خصوصًا لdata حساسة أو key لا ينتقل، وفرق بين storage persistence وبين حماية encryption.

## Trade-offs and decision criteria

Room gives relational power but needs schema evolution. DataStore simplifies small key/value settings but not joins or large datasets. SharedPreferences can be pragmatic for legacy code, but migration should be tested and avoid main-thread I/O.

## Failure modes

Storing thousands of articles as one JSON preference prevents efficient queries and safe partial updates. Assuming DataStore encrypts tokens by default exposes secrets. A destructive Room migration can erase offline drafts.

## Production perspective

An offline news app stores articles and remote keys in Room, theme preference in DataStore, and migrates old SharedPreferences once with tests. Auth credentials follow a dedicated secure storage and server session design.

## Interview answer — short

“Room fits structured relational data and transactions; DataStore fits small asynchronous preferences; SharedPreferences is mainly a legacy key/value API. Storage choice does not automatically encrypt secrets or solve migration.”

## Interview answer — structured

“I use Room when I need tables, indexed queries, relationships, transactions and observable rows. DataStore is a good fit for small settings with asynchronous Flow reads and atomic updates. SharedPreferences may already exist in a legacy app, but I would migrate carefully rather than expanding it for new complex data. I avoid putting a large dataset into one preference blob, and I treat sensitive tokens separately because neither Room nor DataStore is an automatic secret vault.”

## Interview answer — deep senior

The decision is driven by data shape and invariants. Room provides SQLite-backed structured storage, compile-time query checks and transactions, but schema migrations need versioned tests. DataStore provides asynchronous, transactional preference updates and is excellent for theme, onboarding or small typed configuration; it cannot replace relational queries. SharedPreferences is useful for interoperability with legacy code, but synchronous patterns and migration risk make it a poor foundation for new complex storage. For an offline-first feed I store entities and remote keys in Room and observe them through Flow, while DataStore holds a small user preference. I test migration on real old files and explicitly design encryption/backup/session invalidation for sensitive material.

For an order history I need indexed queries, relationships, and atomic multi-row changes, so I choose Room. For a small theme preference I use DataStore, whose Flow and transactional update API suit configuration without building a database schema. SharedPreferences may remain at a legacy boundary, but I would plan migration rather than spreading synchronous access. DataStore is not a relational store and Room is more work than a single preference deserves. The failure case is using key-value storage for hundreds of records or treating persistence as encryption. I review backup rules and sensitive-data policy separately, then test migration and process restart before declaring the change safe.

## How to answer in the interview

- **Why:** Storage choice follows data shape and invariants.
- **How:** Assign order rows to Room and small settings to DataStore.
- **Trade-offs:** Consider schema/migration cost versus transactional preference updates.
- **Failure cases:** Treating DataStore as a database or storage as encryption.
- **Production solution:** Test legacy preference migration, backups and process restart.

## Deep-dive talking points

Compare query complexity, transaction scope, migration and security/backup assumptions.

## Follow-up questions

- [DAT-06](../dat-06/): What does Room add? **Answer:** entity/DAO/schema checks, transactions, migrations and Flow queries.
- [DAT-11](../dat-11/): How protect old data? **Answer:** versioned migration tests and rollback/recovery strategy.

## Self-check rubric

Can I pick storage by shape, name migration risk and reject automatic secret protection?

## References and reviewed-on date

- [Android Room guide](https://developer.android.com/training/data-storage/room) — structured storage.
- [Android DataStore guide](https://developer.android.com/topic/libraries/architecture/datastore) — small settings and migration.

Technically reviewed against linked primary documentation on 2026-10-13. Examples are conceptual unless explicitly stated otherwise; no Android device execution is claimed.
