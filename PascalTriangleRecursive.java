import java.util.Scanner;

/**
 * Prints the Nth line of Pascal's Triangle using recursion.
 *
 * Line numbering is 1-based:
 * line 1 -> 1
 * line 2 -> 1 1
 * line 3 -> 1 2 1
 */
public class PascalTriangleRecursive {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter N (line number): ");
        int n = scanner.nextInt();

        if (n <= 0) {
            System.out.println("N must be a positive integer.");
            return;
        }

        int[] nthLine = getPascalLine(n);
        printLine(nthLine);
    }

    /**
     * Recursively computes the nth line of Pascal's Triangle.
     *
     * @param n line number (1-based)
     * @return array containing values of the nth line
     */
    public static int[] getPascalLine(int n) {
        if (n == 1) {
            return new int[] {1};
        }

        int[] previousLine = getPascalLine(n - 1);
        int[] currentLine = new int[n];

        currentLine[0] = 1;
        currentLine[n - 1] = 1;

        for (int i = 1; i < n - 1; i++) {
            currentLine[i] = previousLine[i - 1] + previousLine[i];
        }

        return currentLine;
    }

    private static void printLine(int[] line) {
        for (int value : line) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}
