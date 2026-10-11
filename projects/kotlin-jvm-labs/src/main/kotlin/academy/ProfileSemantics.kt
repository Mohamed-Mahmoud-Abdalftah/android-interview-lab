package academy

/** Mutable draft for demonstrating reference aliasing and shallow data-class copies. */
data class ProfileDraft(val profileId: String, val tags: MutableList<String>) {
    /** Detaches the list. Strings are immutable, so no nested copy is needed here. */
    fun detachedCopy(): ProfileDraft = copy(tags = tags.toMutableList())
}

/** Stable cache key: both fields participate in generated equals() and hashCode(). */
data class ProfileKey(val tenantId: String, val profileId: String)

/** Normalizes and copies a potentially nullable, mutable Java collection at the boundary. */
fun snapshotLegacyTags(raw: List<String?>?): List<String> =
    raw.orEmpty().mapNotNull { tag -> tag?.trim()?.takeIf { it.isNotEmpty() } }

fun safeTagsFromLegacy(id: String): List<String> {
    // The unannotated Java return and its elements may be null; the list is mutable.
    val raw: List<String?>? = LegacyProfileApi.tagsFor(id)
    return snapshotLegacyTags(raw)
}
