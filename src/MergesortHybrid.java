public final class MergesortHybrid {

    private MergesortHybrid() { }

    public static void sort(int[] a, int cutoff) {
        sort(a, cutoff, false);
    }

    public static void sort(int[] a, int cutoff, boolean skipIfSorted) {
        int[] aux = new int[a.length];
        sort(a, aux, 0, a.length - 1, cutoff, skipIfSorted);
    }

    private static void sort(int[] a, int[] aux, int lo, int hi,
                             int cutoff, boolean skip) {
        if (hi <= lo) return;
        if (hi - lo + 1 <= cutoff) {
            insertionSort(a, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff, skip);
        sort(a, aux, mid + 1, hi, cutoff, skip);
        if (skip && !less(a[mid + 1], a[mid])) return;
        merge(a, aux, lo, mid, hi);
    }

    private static void merge(int[] a, int[] aux, int lo, int mid, int hi) {
        System.arraycopy(a, lo, aux, lo, hi - lo + 1);
        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid)                   a[k] = aux[j++];
            else if (j > hi)               a[k] = aux[i++];
            else if (less(aux[j], aux[i])) a[k] = aux[j++];
            else                           a[k] = aux[i++];
        }
    }

    private static void insertionSort(int[] a, int lo, int hi) {
        for (int i = lo + 1; i <= hi; i++) {
            for (int j = i; j > lo && less(a[j], a[j - 1]); j--) {
                int t = a[j]; a[j] = a[j - 1]; a[j - 1] = t;
            }
        }
    }

    private static boolean less(int v, int w) { return v < w; }

    public static boolean isSorted(int[] a) {
        for (int i = 1; i < a.length; i++) if (a[i] < a[i - 1]) return false;
        return true;
    }

    public static void main(String[] args) {
        java.util.Random r = new java.util.Random(4214);
        for (int n : new int[]{0, 1, 2, 3, 10, 31, 1000, 12345}) {
            for (int c = 0; c <= 30; c++) {
                for (boolean skip : new boolean[]{false, true}) {
                    int[] a = new int[n];
                    for (int i = 0; i < n; i++) a[i] = r.nextInt(50);
                    int[] b = a.clone();
                    java.util.Arrays.sort(b);
                    sort(a, c, skip);
                    if (!java.util.Arrays.equals(a, b))
                        throw new AssertionError("FAIL n=" + n + " cutoff=" + c);
                }
            }
        }
        System.out.println("MergesortHybrid self-test: OK");
    }
}