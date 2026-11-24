import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Locale;

public final class BenchmarkRunner {

    public static void main(String[] args) throws IOException {
        Path out = Paths.get(args.length > 0 ? args[0] : "results/raw_benchmark.csv");
        int m      = args.length > 1 ? Integer.parseInt(args[1]) : 30;
        int warmup = args.length > 2 ? Integer.parseInt(args[2]) : 5;
        int cutMax = args.length > 3 ? Integer.parseInt(args[3]) : 30;
        if (out.getParent() != null) Files.createDirectories(out.getParent());

        int[] w0 = DataGenerator.generate(DataGenerator.Dist.RANDOM, 100_000);
        int[] w1 = new int[w0.length];
        for (int r = 0; r < 30; r++) {
            for (int c : new int[]{0, 7, 10, 25}) {
                System.arraycopy(w0, 0, w1, 0, w0.length);
                MergesortHybrid.sort(w1, c);
            }
        }

        try (BufferedWriter w = Files.newBufferedWriter(out)) {
            w.write("distribution,N,cutoff,run,time_ms\n");
            for (DataGenerator.Dist d : DataGenerator.Dist.values()) {
                for (int n : DataGenerator.SIZES) {
                    int[] base = DataGenerator.generate(d, n);
                    int[] work = new int[n];
                    for (int cutoff = 0; cutoff <= cutMax; cutoff++) {
                        long wEnd = System.nanoTime() + 300_000_000L;
                        int done = 0;
                        while (done < warmup || System.nanoTime() < wEnd) {
                            System.arraycopy(base, 0, work, 0, n);
                            MergesortHybrid.sort(work, cutoff);
                            done++;
                        }
                        StringBuilder sb = new StringBuilder();
                        for (int run = 1; run <= m; run++) {
                            System.arraycopy(base, 0, work, 0, n);
                            System.gc();
                            long t0 = System.nanoTime();
                            MergesortHybrid.sort(work, cutoff);
                            long t1 = System.nanoTime();
                            if (!MergesortHybrid.isSorted(work))
                                throw new IllegalStateException("Ket qua sai");
                            sb.append(d.name()).append(',').append(n).append(',')
                                    .append(cutoff).append(',').append(run).append(',')
                                    .append(String.format(Locale.ROOT, "%.6f", (t1 - t0) / 1e6))
                                    .append('\n');
                        }
                        w.write(sb.toString());
                        w.flush();
                    }
                    System.err.println("xong " + d + " N=" + n);
                }
            }
        }
        System.err.println("HOAN TAT");
    }
}