package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class SaveNoteTest {
    private class RecordingStore : NoteWriter {
        val saved = mutableListOf<Note>()
        override fun upsert(note: Note) { saved += note }
    }

    @Test
    fun validInputIsNormalizedAndDelegatedOnce() {
        val store = RecordingStore()
        val result = SaveNote(store)("  n-1  ", "  Interview prep  ")
        assertEquals(Note("n-1", "Interview prep"), result)
        assertEquals(listOf(result), store.saved)
    }

    @Test
    fun invalidIdDoesNotCallStore() {
        val store = RecordingStore()
        assertThrows(IllegalArgumentException::class.java) { SaveNote(store)("  ", "valid") }
        assertEquals(emptyList<Note>(), store.saved)
    }

    @Test
    fun invalidTitleDoesNotCallStore() {
        val store = RecordingStore()
        assertThrows(IllegalArgumentException::class.java) { SaveNote(store)("n-1", " ") }
        assertEquals(emptyList<Note>(), store.saved)
    }

    @Test
    fun storeFailurePropagatesToCaller() {
        val failing = object : NoteWriter {
            override fun upsert(note: Note) { throw IllegalStateException("disk full") }
        }
        assertThrows(IllegalStateException::class.java) { SaveNote(failing)("n-1", "Valid") }
    }
}
