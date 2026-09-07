from app.core.student import Student


def test_student_creation():
    student = Student("Test Student")

    assert student.name == "Test Student"
    assert student.level == "beginner"


def test_student_skills_start_at_zero():
    student = Student("Test Student")

    for skill in student.skills.values():
        assert skill == 0.0