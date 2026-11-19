from exceptions import InputDataError, NotFoundError
from models import Course, Enrollment, Instructor, Lesson, Student, User


class PlatformManager:
    def __init__(self) -> None:
        self.users: dict[int, User] = {}
        self.courses: dict[int, Course] = {}
        self.enrollments: dict[int, Enrollment] = {}

    def reset(self) -> None:
        self.users.clear()
        self.courses.clear()
        self.enrollments.clear()

    # Пользователи (CRUD)
    def add_user(self, user: User) -> None:
        if user.user_id in self.users:
            raise InputDataError("Пользователь с таким ID уже есть")
        self.users[user.user_id] = user

    def get_user(self, user_id: int) -> User:
        if user_id not in self.users:
            raise NotFoundError("Пользователь не найден")
        return self.users[user_id]

    def update_user_name(self, user_id: int, new_name: str) -> None:
        user = self.get_user(user_id)
        if not new_name.strip():
            raise InputDataError("Имя не может быть пустым")
        user.name = new_name.strip()

    def delete_user(self, user_id: int) -> None:
        self.get_user(user_id)
        for c in self.courses.values():
            if c.teacher_id == user_id:
                raise InputDataError("Нельзя удалить преподавателя, у которого есть курсы")
        for e in self.enrollments.values():
            if e.student_id == user_id:
                raise InputDataError("Нельзя удалить студента, записанного на курс")
        del self.users[user_id]

    # Курсы (CRUD)
    def add_course(self, course: Course) -> None:
        if course.course_id in self.courses:
            raise InputDataError("Курс с таким ID уже существует")
        teacher = self.get_user(course.teacher_id)
        if not isinstance(teacher, Instructor):
            raise InputDataError("Указанный ID не принадлежит преподавателю")
        self.courses[course.course_id] = course

    def get_course(self, course_id: int) -> Course:
        if course_id not in self.courses:
            raise NotFoundError("Курс не найден")
        return self.courses[course_id]

    def update_course_price(self, course_id: int, new_price: float) -> None:
        course = self.get_course(course_id)
        if new_price < 0:
            raise InputDataError("Цена не может быть меньше 0")
        course.price = float(new_price)

    def delete_course(self, course_id: int) -> None:
        self.get_course(course_id)
        for e in self.enrollments.values():
            if e.course_id == course_id:
                raise InputDataError("Нельзя удалить курс, на который записаны студенты")
        del self.courses[course_id]

    def add_lesson(self, course_id: int, lesson: Lesson) -> None:
        course = self.get_course(course_id)
        course.add_lesson(lesson)

    # Записи на курсы (CRUD)
    def add_enrollment(self, enrollment: Enrollment) -> None:
        if enrollment.enroll_id in self.enrollments:
            raise InputDataError("Запись с таким ID уже есть")
        student = self.get_user(enrollment.student_id)
        if not isinstance(student, Student):
            raise InputDataError("Записывать на курс можно только студентов")
        self.get_course(enrollment.course_id)
        self.enrollments[enrollment.enroll_id] = enrollment

    def mark_lesson_done(self, enroll_id: int, lesson_id: int) -> None:
        if enroll_id not in self.enrollments:
            raise NotFoundError("Запись на курс не найдена")
        enroll = self.enrollments[enroll_id]
        course = self.get_course(enroll.course_id)

        lesson_ids = [item.lesson_id for item in course.lessons]
        if lesson_id not in lesson_ids:
            raise NotFoundError("Такого урока нет в этом курсе")
        enroll.finish_lesson(lesson_id)

    def delete_enrollment(self, enroll_id: int) -> None:
        if enroll_id not in self.enrollments:
            raise NotFoundError("Запись на курс не найдена")
        del self.enrollments[enroll_id]
