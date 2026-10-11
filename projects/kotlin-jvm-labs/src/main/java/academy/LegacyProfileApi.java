package academy;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Simulates an unannotated Java SDK contract. These are demo values only. */
public final class LegacyProfileApi {
    private LegacyProfileApi() {}

    public static String nameFor(String id) {
        if ("ada".equals(id)) return " Ada ";
        if ("blank".equals(id)) return "   ";
        return null;
    }

    /** Returns a mutable Java collection with deliberately unannotated nulls. */
    public static List<String> tagsFor(String id) {
        if (!"mona".equals(id)) return null;
        return new ArrayList<>(Arrays.asList("  kotlin  ", null, " ", "android"));
    }
}
