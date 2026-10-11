package academy

enum class NoteSync { CLEAN, PENDING, CONFLICT }

data class RemoteNote(val id: String, val title: String, val version: Long)

data class LocalNote(
    val id: String,
    val title: String,
    val serverVersion: Long?,
    val sync: NoteSync,
    val pendingMutationId: String?,
    val remoteConflict: RemoteNote? = null,
)

sealed interface RemotePush {
    data class Accepted(val note: RemoteNote) : RemotePush
    data class Conflict(val current: RemoteNote) : RemotePush
}

fun interface NotesRemote {
    fun upsert(mutationId: String, id: String, title: String, baseVersion: Long?): RemotePush
}

/** In-memory teaching model; a real offline source of truth must survive process death. */
class OfflineNotesRepository(
    private val remote: NotesRemote,
    private val nextMutationId: () -> String,
) {
    private val local = linkedMapOf<String, LocalNote>()

    fun get(id: String): LocalNote? = local[id]
    fun all(): List<LocalNote> = local.values.toList()

    fun seed(note: RemoteNote) {
        require(note.id.isNotBlank() && note.title.isNotBlank() && note.version >= 0)
        local[note.id] = LocalNote(note.id, note.title, note.version, NoteSync.CLEAN, null)
    }

    fun saveLocal(rawId: String, rawTitle: String) {
        val id = rawId.trim()
        val title = rawTitle.trim()
        require(id.isNotEmpty() && title.isNotEmpty())
        val current = local[id]
        local[id] = LocalNote(
            id = id,
            title = title,
            serverVersion = current?.serverVersion,
            sync = NoteSync.PENDING,
            pendingMutationId = nextMutationId(),
        )
    }

    fun sync(id: String) {
        val pending = local[id]?.takeIf { it.sync == NoteSync.PENDING } ?: return
        val mutationId = requireNotNull(pending.pendingMutationId)
        when (val result = remote.upsert(mutationId, pending.id, pending.title, pending.serverVersion)) {
            is RemotePush.Accepted -> {
                require(result.note.id == pending.id)
                local[id] = LocalNote(result.note.id, result.note.title, result.note.version, NoteSync.CLEAN, null)
            }
            is RemotePush.Conflict -> {
                require(result.current.id == pending.id)
                local[id] = pending.copy(sync = NoteSync.CONFLICT, remoteConflict = result.current)
            }
        }
    }
}
