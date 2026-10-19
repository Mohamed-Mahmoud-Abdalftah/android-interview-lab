package academy

import interviewlab.kot_10.ParserHolder
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class LazyLateinitSnippetTest {
    @Test
    fun `lazy computes on first read and lateinit requires assignment`() {
        val holder = ParserHolder()
        assertEquals(0, holder.constructionCount)
        assertFalse(holder.labelReady())
        assertFailsWith<UninitializedPropertyAccessException> { holder.label }

        assertTrue(holder.parser.matches("ABC"))
        assertTrue(holder.parser.matches("XYZ"))
        assertEquals(1, holder.constructionCount)

        holder.label = "Ready"
        assertTrue(holder.labelReady())
        assertEquals("Ready", holder.label)
    }
}
