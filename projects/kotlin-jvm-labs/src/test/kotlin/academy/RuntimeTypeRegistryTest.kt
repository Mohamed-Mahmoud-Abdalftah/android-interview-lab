package academy

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class RuntimeTypeRegistryTest {
    open class Animal(val name: String)
    class Cat(name: String) : Animal(name)

    @Test fun reifiedFactoryKeepsARealRuntimeTypeToken() {
        val key = typeKey<String>("display-name")
        assertEquals(String::class, key.type)
    }

    @Test fun valuesRoundTripWithoutAnUncheckedCastAtTheCallSite() {
        val registry = RuntimeTypeRegistry()
        val retries = typeKey<Int>("retries")
        registry.put(retries, 3)
        assertEquals(3, registry.get(retries))
    }

    @Test fun sameNameCanHaveDifferentExplicitRuntimeTypes() {
        val registry = RuntimeTypeRegistry()
        registry.put(typeKey<Int>("value"), 7)
        registry.put(typeKey<String>("value"), "seven")
        assertEquals(7, registry.get(typeKey<Int>("value")))
        assertEquals("seven", registry.get(typeKey<String>("value")))
    }

    @Test fun unknownBoundaryRejectsAValueThatDoesNotMatchItsToken() {
        val registry = RuntimeTypeRegistry()
        assertFalse(registry.putUnknown(typeKey<Int>("count"), "three"))
        assertNull(registry.get(typeKey<Int>("count")))
        assertTrue(registry.putUnknown(typeKey<Int>("count"), 3))
        assertEquals(3, registry.get(typeKey<Int>("count")))
    }

    @Test fun missingKeyReturnsNullInsteadOfInventingADefault() {
        assertNull(RuntimeTypeRegistry().get(typeKey<String>("missing")))
    }

    @Test fun covariantProducerCanBeReadThroughABroaderType() {
        val cats: Producer<Cat> = Producer { Cat("Misho") }
        val animals: Producer<Animal> = cats
        assertEquals("Misho", animals.produce().name)
    }

    @Test fun contravariantConsumerCanAcceptANarrowerType() {
        val names = mutableListOf<String>()
        val animals: Consumer<Animal> = Consumer { names += it.name }
        val cats: Consumer<Cat> = animals
        cats.accept(Cat("Lulu"))
        assertEquals(listOf("Lulu"), names)
    }
}
