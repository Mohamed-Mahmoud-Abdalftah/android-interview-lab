# Day 13 optional speaking — lifecycle ownership

Read [AND-001](../03-Android-Internals/and-001-activity-fragment-and-view-lifecycle.md). Ten minutes of guided speaking; no audio or pronunciation feedback is claimed.

**Pacing:** “A Fragment may outlive its view / so view updates use the view lifecycle owner / and process death may skip onDestroy.” Stress **outlive**, **view owner**, **may skip**.

**About 20 seconds:** “I tie a view observer to the Fragment view lifecycle and clear binding references at onDestroyView. I choose Activity resource boundaries by visibility needs and never depend on onDestroy for process-death persistence.”

**About 90 seconds:** “The Activity lifecycle has callbacks for creation, visibility and foreground interaction, but a resource's start and stop points depend on the product and API. A Fragment owns a separate view lifecycle. If an observer updates a binding, I use viewLifecycleOwner so the observer stops with that view; I clear the reference at onDestroyView and rebind a new view separately. A ViewModel can retain some in-memory state across configuration changes, but process death is different, and onDestroy is not guaranteed. Saved UI state and durable data storage solve different recovery needs. Our JVM test only checks detach and rebind behavior; Android navigation and process recreation need platform tests.”

**Useful phrases:** “view lifecycle owner”, “retained view reference”, “configuration change”, “system-initiated process death”. Avoid “onDestroy always runs”.

**Self-check:** Explain one Fragment-view bug and one process-death rule without notes. Retry with [revision cards](../Flashcards-Revision/AND-001.md). Free written source: [Android Fragment lifecycle](https://developer.android.com/guide/fragments/lifecycle), checked 2026-10-10.
