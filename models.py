from exceptions import InputDataError


class User:
    def __init__(self, user_id: int, name: str, email: str) -> None:
        if user_id <= 0:
            raise InputDataError("ID должен быть больше 0")
        if not name.strip():
            raise InputDataError("Имя не может быть пустым")
        if "@" not in email:
            raise InputDataError("Неверный формат почты")

        self.user_id: int = user_id
        self.name: str = name.strip()
        self.email: str = email.strip()

    def get_role(self) -> str:
        return "user"

    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "role": self.get_role(),
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
        }


class Student(User):
    def __init__(self, user_id: int, name: str, email: str, level: str) -> None:
        super().__init__(user_id, name, email)
        self.level: str = level.strip() or "Beginner"

    def get_role(self) -> str:
        return "student"

    def to_dict(self) -> dict[str, str | int | float]:
        data = super().to_dict()
        data["level"] = self.level
        return data


class Instructor(User):
    def __init__(
        self, user_id: int, name: str, email: str, subject: str, rating: float
    ) -> None:
        super().__init__(user_id, name, email)
        if not (0 <= rating <= 5):
            raise InputDataError("Рейтинг должен быть от 0 до 5")
        self.subject: str = subject.strip()
        self.rating: float = rating

    def get_role(self) -> str:
        return "instructor"

    def to_dict(self) -> dict[str, str | int | float]:
        data = super().to_dict()
        data["subject"] = self.subject
        data["rating"] = self.rating
        return data


class Lesson:
    def __init__(self, lesson_id: int, title: str, minutes: int) -> None:
        if lesson_id <= 0 or minutes <= 0:
            raise InputDataError("ID и длительность должны быть больше 0")
        if not title.strip():
            raise InputDataError("Название урока не может быть пустым")

        self.lesson_id: int = lesson_id
        self.title: str = title.strip()
        self.minutes: int = minutes

    def get_type(self) -> str:
        return "lesson"

    def to_dict(self) -> dict[str, str | int]:
        return {
            "type": self.get_type(),
            "lesson_id": self.lesson_id,
            "title": self.title,
            "minutes": self.minutes,
        }


class VideoLesson(Lesson):
    def __init__(
        self, lesson_id: int, title: str, minutes: int, url: str, quality: str = "1080p"
    ) -> None:
        super().__init__(lesson_id, title, minutes)
        if not url.strip():
            raise InputDataError("Ссылка на видео не указана")
        self.url: str = url.strip()
        self.quality: str = quality

    def get_type(self) -> str:
        return "video"

    def to_dict(self) -> dict[str, str | int]:
        data = super().to_dict()
        data["url"] = self.url
        data["quality"] = self.quality
        return data


class QuizLesson(Lesson):
    def __init__(
        self, lesson_id: int, title: str, minutes: int, questions: int, pass_score: int
    ) -> None:
        super().__init__(lesson_id, title, minutes)
        if questions <= 0 or pass_score < 0 or pass_score > questions:
            raise InputDataError("Неверные настройки теста")
        self.questions: int = questions
        self.pass_score: int = pass_score

    def get_type(self) -> str:
        return "quiz"

    def to_dict(self) -> dict[str, str | int]:
        data = super().to_dict()
        data["questions"] = self.questions
        data["pass_score"] = self.pass_score
        return data


class Course:
    def __init__(
        self,
        course_id: int,
        title: str,
        price: float,
        teacher_id: int,
        lessons: list[Lesson] | None = None,
    ) -> None:
        if course_id <= 0:
            raise InputDataError("ID курса должен быть больше 0")
        if not title.strip():
            raise InputDataError("Название курса пустое")
        if price < 0:
            raise InputDataError("Цена не может быть меньше 0")

        self.course_id: int = course_id
        self.title: str = title.strip()
        self.price: float = float(price)
        self.teacher_id: int = teacher_id
        self.lessons: list[Lesson] = lessons if lessons is not None else []

    def add_lesson(self, lesson: Lesson) -> None:
        for item in self.lessons:
            if item.lesson_id == lesson.lesson_id:
                raise InputDataError("Урок с таким ID уже есть в курсе")
        self.lessons.append(lesson)

    def get_total_time(self) -> int:
        total = 0
        for lesson in self.lessons:
            total += lesson.minutes
        return total


class Enrollment:
    def __init__(
        self,
        enroll_id: int,
        student_id: int,
        course_id: int,
        done_lessons: list[int] | None = None,
    ) -> None:
        if enroll_id <= 0:
            raise InputDataError("ID записи должен быть больше 0")
        self.enroll_id: int = enroll_id
        self.student_id: int = student_id
        self.course_id: int = course_id
        self.done_lessons: list[int] = done_lessons if done_lessons is not None else []

    def finish_lesson(self, lesson_id: int) -> None:
        if lesson_id not in self.done_lessons:
            self.done_lessons.append(lesson_id)
