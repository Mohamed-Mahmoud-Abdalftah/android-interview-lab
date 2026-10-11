package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class OfflineNotesRepositoryTest {
    @Test fun localWriteIsImmediatelyReadableAndPending() {
        val repository = OfflineNotesRepository(remote = { _, _, _, _ -> error("not called") }, nextMutationId = { "m-1" })
        repository.saveLocal("n-1", "  Draft  ")
        assertEquals(LocalNote("n-1", "Draft", null, NoteSync.PENDING, "m-1"), repository.get("n-1"))
    }

    @Test fun acceptedSyncReplacesLocalWithCanonicalCleanRecord() {
        val remote = NotesRemote { _, id, _, _ -> RemotePush.Accepted(RemoteNote(id, "Server title", 7)) }
        val repository = OfflineNotesRepository(remote, nextMutationId = { "m-2" })
        repository.saveLocal("n-2", "Draft")
        repository.sync("n-2")
        assertEquals(LocalNote("n-2", "Server title", 7, NoteSync.CLEAN, null), repository.get("n-2"))
    }

    @Test fun transportFailureKeepsPendingMutationForRetryWithSameIdentity() {
        val calls = mutableListOf<String>()
        var fail = true
        val remote = NotesRemote { mutationId, id, title, _ ->
            calls += mutationId
            if (fail) error("offline") else RemotePush.Accepted(RemoteNote(id, title, 1))
        }
        val repository = OfflineNotesRepository(remote, nextMutationId = { "stable-id" })
        repository.saveLocal("n-3", "Draft")
        assertThrows(IllegalStateException::class.java) { repository.sync("n-3") }
        assertEquals(NoteSync.PENDING, repository.get("n-3")?.sync)
        fail = false
        repository.sync("n-3")
        assertEquals(listOf("stable-id", "stable-id"), calls)
    }

    @Test fun conflictPreservesLocalDraftAndStoresRemoteEvidence() {
        val server = RemoteNote("n-4", "Remote edit", 4)
        val repository = OfflineNotesRepository(
            remote = { _, _, _, _ -> RemotePush.Conflict(server) },
            nextMutationId = { "m-4" },
        )
        repository.seed(RemoteNote("n-4", "Old", 3))
        repository.saveLocal("n-4", "My edit")
        repository.sync("n-4")
        assertEquals(LocalNote("n-4", "My edit", 3, NoteSync.CONFLICT, "m-4", server), repository.get("n-4"))
    }

    @Test fun secondLocalEditGetsNewMutationButKeepsBaseServerVersion() {
        var next = 0
        val repository = OfflineNotesRepository(remote = { _, _, _, _ -> error("not called") }, nextMutationId = { "m-${++next}" })
        repository.seed(RemoteNote("n-5", "Server", 9))
        repository.saveLocal("n-5", "first")
        repository.saveLocal("n-5", "second")
        assertEquals(LocalNote("n-5", "second", 9, NoteSync.PENDING, "m-2"), repository.get("n-5"))
    }

    @Test fun blankIdentityOrTitleIsRejectedWithoutLocalMutation() {
        val repository = OfflineNotesRepository(remote = { _, _, _, _ -> error("not called") }, nextMutationId = { "m" })
        assertThrows(IllegalArgumentException::class.java) { repository.saveLocal(" ", "title") }
        assertThrows(IllegalArgumentException::class.java) { repository.saveLocal("n", " ") }
        assertEquals(emptyList<LocalNote>(), repository.all())
    }
}
