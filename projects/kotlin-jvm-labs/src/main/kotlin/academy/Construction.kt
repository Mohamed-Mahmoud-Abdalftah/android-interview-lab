package academy

/** Records the documented source-order execution of property initializers and init blocks. */
class ConstructionTimeline(raw: String, private val events: MutableList<String>) {
    private val normalized = raw.trim().also { events += "property:$it" }

    init {
        events += "init"
        require(normalized.isNotEmpty()) { "A name is required" }
    }

    val label: String = normalized.uppercase().also { events += "label:$it" }

    constructor(raw: String, events: MutableList<String>, prefix: String) : this(raw, events) {
        events += "secondary:$prefix"
    }
}

/** Demonstrates one invariant-preserving construction boundary without generated copy(). */
class EndpointConfig private constructor(val host: String, val port: Int) {
    init {
        require(host.isNotBlank())
        require(port in 1..65535)
    }

    fun authority(): String = "$host:$port"

    companion object {
        fun parse(rawHost: String?, port: Int): EndpointConfig? {
            val host = rawHost?.trim()?.takeIf { it.isNotEmpty() } ?: return null
            if (port !in 1..65535) return null
            return EndpointConfig(host, port)
        }
    }
}
