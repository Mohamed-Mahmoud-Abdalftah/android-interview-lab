package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertNotSame
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class ProfileSemanticsTest {
    @Test
    fun `val binding can still expose mutable tags`() {
        val draft = ProfileDraft("p-1", mutableListOf("android"))

        draft.tags.add("kotlin")

        assertEquals(listOf("android", "kotlin"), draft.tags)
    }

    @Test
    fun `data class copy shares a mutable tag list`() {
        val original = ProfileDraft("p-1", mutableListOf("android"))
        val shallowCopy = original.copy()

        shallowCopy.tags.add("kotlin")

        assertNotSame(original, shallowCopy)
        assertEquals(listOf("android", "kotlin"), original.tags)
    }

    @Test
    fun `detached copy prevents copied tags from changing original`() {
        val original = ProfileDraft("p-1", mutableListOf("android"))
        val detached = original.detachedCopy()

        detached.tags.add("kotlin")

        assertEquals(listOf("android"), original.tags)
        assertEquals(listOf("android", "kotlin"), detached.tags)
    }

    @Test
    fun `detached copy prevents original tags from changing copy`() {
        val original = ProfileDraft("p-1", mutableListOf("android"))
        val detached = original.detachedCopy()

        original.tags.add("kotlin")

        assertEquals(listOf("android", "kotlin"), original.tags)
        assertEquals(listOf("android"), detached.tags)
    }

    @Test
    fun `var can select a different profile without mutating the first`() {
        val first = ProfileKey("acme", "p-1")
        var selected = first

        selected = ProfileKey("acme", "p-2")

        assertEquals("p-1", first.profileId)
        assertEquals("p-2", selected.profileId)
    }

    @Test
    fun `equal profile keys can be different objects`() {
        val first = ProfileKey("acme", "p-1")
        val second = ProfileKey("acme", "p-1")

        assertEquals(first, second)
        assertFalse(first === second)
    }

    @Test
    fun `equal immutable keys have equal hashes and retrieve the same map entry`() {
        val stored = ProfileKey("acme", "p-1")
        val equivalent = ProfileKey("acme", "p-1")
        val cache = mapOf(stored to "Ada")

        assertEquals(stored.hashCode(), equivalent.hashCode())
        assertEquals("Ada", cache[equivalent])
    }

    @ParameterizedTest(name = "key differs for tenant={0}, profile={1}")
    @CsvSource("other, p-1", "acme, p-2")
    fun `changing either key field changes equality`(tenantId: String, profileId: String) {
        assertNotEquals(ProfileKey("acme", "p-1"), ProfileKey(tenantId, profileId))
    }

    @Test
    fun `missing Java tags become an empty snapshot`() {
        assertEquals(emptyList<String>(), safeTagsFromLegacy("missing"))
    }

    @Test
    fun `Java tags are trimmed and null or blank elements removed`() {
        assertEquals(listOf("kotlin", "android"), safeTagsFromLegacy("mona"))
    }

    @Test
    fun `snapshot does not change when caller mutates Java list`() {
        val javaTags = LegacyProfileApi.tagsFor("mona")
        val snapshot = snapshotLegacyTags(javaTags)

        javaTags.add("later")

        assertEquals(listOf("kotlin", "android"), snapshot)
        assertEquals(5, javaTags.size)
    }

    @Test
    fun `all invalid tags produce an empty snapshot`() {
        assertEquals(emptyList<String>(), snapshotLegacyTags(listOf(null, " \t ")))
    }
}
