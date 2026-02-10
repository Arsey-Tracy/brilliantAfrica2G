from ussd.models import Role, Student

def get_student_menu(student: Student) -> str:
    return (
        f"CON Welcome back {student.first_name}!\n"
        "1. Tutor Chat\n"
        "2. Performance Review\n"
        "3. Subscriptions and Plans\n"
        "4. Help & Support\n"
        "5. About BrilliantAfrica Tutor\n"
    )