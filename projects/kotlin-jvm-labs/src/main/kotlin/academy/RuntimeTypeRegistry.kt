package academy

import kotlin.reflect.KClass

data class TypeKey<T : Any>(val name: String, val type: KClass<T>) {
    init {
        require(name.isNotBlank()) { "A type key needs a stable name" }
    }
}

inline fun <reified T : Any> typeKey(name: String): TypeKey<T> = TypeKey(name, T::class)

class RuntimeTypeRegistry {
    private val values = mutableMapOf<TypeKey<*>, Any>()

    fun <T : Any> put(key: TypeKey<T>, value: T) {
        values[key] = value
    }

    fun putUnknown(key: TypeKey<*>, value: Any): Boolean {
        if (!key.type.isInstance(value)) return false
        values[key] = value
        return true
    }

    fun <T : Any> get(key: TypeKey<T>): T? {
        val value = values[key] ?: return null
        check(key.type.isInstance(value)) { "Registry invariant was violated for ${key.name}" }
        @Suppress("UNCHECKED_CAST")
        return value as T
    }
}

fun interface Producer<out T> {
    fun produce(): T
}

fun interface Consumer<in T> {
    fun accept(value: T)
}
