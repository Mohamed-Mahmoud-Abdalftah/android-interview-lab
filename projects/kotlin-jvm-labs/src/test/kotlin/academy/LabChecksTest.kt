package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class LabChecksTest {
    @ParameterizedTest(name = "legacy id {0} has safe label {1}")
    @CsvSource(
        "ada, Ada",
        "missing, Guest",
        "blank, Guest",
        "unknown, Guest",
    )
    fun `safe label handles Java SDK results`(id: String, expected: String) {
        assertEquals(expected, safeLabelFromLegacy(id))
    }

    @Test
    fun `null cannot become a profile name`() {
        assertNull(ProfileName.parse(null))
    }

    @Test
    fun `whitespace cannot become a profile name`() {
        assertNull(ProfileName.parse(" \t "))
    }

    @Test
    fun `profile name is trimmed`() {
        assertEquals("Mona", ProfileName.parse(" Mona ")?.value)
    }

    @Test
    fun `dereferencing an unchecked Java platform type throws`() {
        // Educational contrast with safeLabelFromLegacy: Java has no nullability annotation here.
        assertThrows<NullPointerException> {
            LegacyProfileApi.nameFor("missing").length
        }
    }
}
