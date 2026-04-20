from utilities.choices import ChoiceSet


class ValidationStatusChoices(ChoiceSet):
    UNKNOWN = "unknown"
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

    CHOICES = [
        (UNKNOWN, "Unknown", "gray"),
        (PASS, "Pass", "green"),
        (WARNING, "Warning", "yellow"),
        (FAIL, "Fail", "red"),
    ]
