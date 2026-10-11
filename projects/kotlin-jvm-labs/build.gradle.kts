plugins {
    kotlin("jvm") version "2.4.20"
    application
}

kotlin { jvmToolchain(17) }
application { mainClass.set("academy.MainKt") }

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.11.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.11.0")
    testImplementation(platform("org.junit:junit-bom:5.14.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
    testLogging { events("passed", "skipped", "failed") }
}

// Compile the exact JVM Kotlin fences from reviewed Interview Lab records.
val labSnippetOutput = layout.buildDirectory.dir("generated/interview-lab-snippets")
val generateLabSnippets by tasks.registering {
    outputs.dir(labSnippetOutput)
    doLast {
        val output = labSnippetOutput.get().asFile
        output.mkdirs()
        val bank = projectDir.resolve("../../Interview-Lab/questions")
        for (id in listOf("COR-01", "COR-02", "FLO-06", "PAY-02")) {
            val markdown = bank.resolve("$id.md").readText()
            val snippet = Regex("```kotlin\\n([\\s\\S]*?)```").find(markdown)?.groupValues?.get(1)
                ?: error("Missing Kotlin example in $id")
            output.resolve("${id.replace('-', '_')}.kt").writeText(snippet)
        }
    }
}
sourceSets.test { kotlin.srcDir(labSnippetOutput) }
tasks.named("compileTestKotlin") { dependsOn(generateLabSnippets) }
