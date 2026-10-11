package academy

data class Note(val id: String, val title: String)

/** Narrow port owned by the caller; storage adapters supply the implementation. */
fun interface NoteWriter {
    fun upsert(note: Note)
}

/** Product rule and delegation; deliberately knows no database or Android type. */
class SaveNote(private val writer: NoteWriter) {
    operator fun invoke(rawId: String, rawTitle: String): Note {
        val id = rawId.trim()
        val title = rawTitle.trim()
        require(id.isNotEmpty()) { "Note ID must not be blank" }
        require(title.isNotEmpty()) { "Note title must not be blank" }
        return Note(id, title).also(writer::upsert)
    }
}
