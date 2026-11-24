import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Random;

public final class DataGenerator {

    public static final long SEED = 4214L;
    public static final int MAX_VALUE = 1_000_000_000;
    public static final int DUP_DISTINCT = 100;
    public static final int[] SIZES = {1_000, 10_000, 100_000, 1_000_000};

    public enum Dist { RANDOM, ASCENDING, DESCENDING, DUPLICATES }

    private DataGenerator() { }

    public static int[] generate(Dist d, int n) {
        Random rnd = new Random(SEED);
        int[] a = new int[n];
        switch (d) {
            case RANDOM:
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(MAX_VALUE + 1);
                break;
            case ASCENDING:
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(MAX_VALUE + 1);
                Arrays.sort(a);
                break;
            case DESCENDING:
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(MAX_VALUE + 1);
                Arrays.sort(a);
                for (int i = 0, j = n - 1; i < j; i++, j--) {
                    int t = a[i]; a[i] = a[j]; a[j] = t;
                }
                break;
            case DUPLICATES:
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(DUP_DISTINCT);
                break;
        }
        return a;
    }

    public static void main(String[] args) throws IOException {
        Path dir = Paths.get(args.length > 0 ? args[0] : "data");
        Files.createDirectories(dir);
        for (Dist d : Dist.values()) {
            for (int n : SIZES) {
                int[] a = generate(d, n);
                Path f = dir.resolve(d.name().toLowerCase() + "_" + n + ".txt");
                try (BufferedWriter w = Files.newBufferedWriter(f)) {
                    for (int v : a) { w.write(Integer.toString(v)); w.write('\n'); }
                }
                System.out.println("wrote " + f);
            }
        }
    }
}