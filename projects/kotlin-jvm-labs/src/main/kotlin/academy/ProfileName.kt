package academy

/** A validated display value. Null means no usable name was supplied. */
class ProfileName private constructor(val value: String) {
    companion object {
        fun parse(raw: String?): ProfileName? {
            val normalized = raw?.trim()?.takeIf { it.isNotEmpty() } ?: return null
            return ProfileName(normalized)
        }
    }
}

fun safeLabelFromLegacy(id: String): String {
    // Explicit nullable type makes the Java uncertainty visible at this boundary.
    val raw: String? = LegacyProfileApi.nameFor(id)
    return ProfileName.parse(raw)?.value ?: "Guest"
}
