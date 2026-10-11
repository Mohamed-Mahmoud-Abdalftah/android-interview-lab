package academy

/** Pure JVM teaching model for view-owner cleanup; not an Android LifecycleOwner. */
class ViewSession {
    private var renderer: ((String) -> Unit)? = null

    fun attach(render: (String) -> Unit) {
        check(renderer == null) { "Detach the previous view first" }
        renderer = render
    }

    fun detach() {
        renderer = null
    }

    fun show(value: String): Boolean {
        val current = renderer ?: return false
        current(value)
        return true
    }
}
