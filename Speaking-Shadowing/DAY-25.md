# Day 25 optional speaking — RecyclerView and view ownership

Read [UI-001](../05-Views-Compose/ui-001-views-recyclerview-and-fragment-binding.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “The adapter binds reusable holders / identity is not the same as content / and a Fragment view has its own lifetime.” Stress **identity** and **view lifetime**.

**About 20 seconds:** “I give each row a stable domain identity, compare visible content separately, and submit a new list. In a Fragment, I clear the binding at onDestroyView and use the view lifecycle owner for rendering.”

**About 90 seconds:** “RecyclerView uses a LayoutManager for positioning and an Adapter to create and bind reusable ViewHolders. A ListAdapter can calculate diffs, but the app must define a correct item callback. A note with the same ID and a new title is the same logical item with changed content. I submit a new list rather than mutating a displayed one, and I consider whether nested fields are mutable. A Fragment can outlive its view, so rendering observers use viewLifecycleOwner and the binding is cleared at onDestroyView. Our JVM tests only verify row comparison and list detachment; an AndroidX adapter, navigation and accessibility still need platform tests.”

**Useful phrases:** “stable item identity”, “visible content comparison”, “submitted list”, “view lifecycle owner”. Avoid “same title means same row”.

**Self-check:** Explain one stale-title cause and one stale-binding cause separately. Retry with [revision cards](../Flashcards-Revision/UI-001.md). Free written references: [RecyclerView](https://developer.android.com/develop/ui/views/layout/recyclerview) and [view binding](https://developer.android.com/topic/libraries/view-binding), checked 2026-10-10.
