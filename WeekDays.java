import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class WeekDays {
    public static void main(String[] args) {
        String[] weekDays = {
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        };

        System.out.println("All days of the week:");
        printDays(weekDays);

        // Resize the array to 5 elements and copy only weekdays (Monday to Friday).
        String[] weekdaysOnly = Arrays.copyOf(weekDays, 5);

        System.out.println("\nWeekdays only:");
        printDays(weekdaysOnly);

        shuffleDays(weekdaysOnly);
        System.out.println("\nShuffled weekdays:");
        printDays(weekdaysOnly);
    }

    private static void printDays(String[] days) {
        for (String day : days) {
            System.out.println(day);
        }
    }

    private static void shuffleDays(String[] days) {
        List<String> dayList = Arrays.asList(days);
        Collections.shuffle(dayList);
    }
}
