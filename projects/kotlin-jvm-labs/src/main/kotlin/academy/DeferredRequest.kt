package academy

/**
 * Builds a callback without reading currentId yet. Each invocation captures one value,
 * normalizes it, then delegates. This does not synchronize concurrent provider updates.
 */
fun createDeferredProfileRequest(
    currentId: () -> String?,
    request: (String) -> Unit,
): () -> Boolean = {
    val id = currentId()?.trim()?.takeIf { it.isNotEmpty() }
    if (id == null) {
        false
    } else {
        request(id)
        true
    }
}
