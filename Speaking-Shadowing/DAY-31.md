# Day 31 optional speaking — storage compatibility

Read [PRO-001](../06-Production-Engineering/pro-001-room-migrations-wal-and-datastore.md).

**20 seconds:** “I treat the local schema as a compatibility contract. Every supported starting version needs a tested migration path with data assertions.”

**90 seconds:** “For a database release, I inventory supported installed schema versions and test every path to the target using exported schemas and realistic rows. I keep related local writes inside short transactions and network calls outside them. WAL improves overlap between readers and a writer but does not remove write contention. I choose Room for relational, queryable state and DataStore for small settings. A graph audit catches missing paths early, while Android migration tests are still required to execute SQL and validate the final Room schema.”

<p dir="rtl" lang="ar"><strong>راجع نفسك:</strong> اشرح ليه نجاح fresh install لا يثبت upgrade، وليه rollback binary ممكن يفشل بعد schema migration.</p>
