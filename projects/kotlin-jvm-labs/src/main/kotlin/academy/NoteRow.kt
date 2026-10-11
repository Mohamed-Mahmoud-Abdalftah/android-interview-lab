package academy

/** Pure JVM row policy; not AndroidX DiffUtil or a RecyclerView adapter. */
data class NoteRow(val id: String, val title: String)

fun sameRow(old: NoteRow, new: NoteRow): Boolean = old.id == new.id

fun sameRowContent(old: NoteRow, new: NoteRow): Boolean = old == new

fun snapshotRows(rows: List<NoteRow>): List<NoteRow> = rows.toList()
