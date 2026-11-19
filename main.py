import json
import xml.etree.ElementTree as ET
from exceptions import PlatformError
from file_worker import FileWorker
from models import Course, Enrollment, Instructor, QuizLesson, Student, VideoLesson
from platform_manager import PlatformManager


def fill_test_data(manager: PlatformManager) -> None:
    manager.add_user(Instructor(1, "Соколов Дмитрий", "sokolov@edu.ru", "Python", 4.8))
    manager.add_user(Student(2, "Козлова Мария", "kozlova@mail.ru", "Beginner"))

    c1 = Course(10, "Основы Python", 3500.0, 1)
    c1.add_lesson(VideoLesson(1, "Классы и объекты", 40, "https://edu.ru"))
    c1.add_lesson(QuizLesson(2, "Проверка знаний по ООП", 15, 10, 8))
    manager.add_course(c1)

    manager.add_enrollment(Enrollment(100, 2, 10))


def show_menu() -> None:
    print("\n Онлайн-платформа обучения ")
    print("1. Список пользователей")
    print("2. Список курсов и уроков")
    print("3. Список записей студентов")
    print("4. Добавить студента")
    print("5. Добавить преподавателя")
    print("6. Изменить имя пользователя")
    print("7. Удалить пользователя")
    print("8. Создать курс")
    print("9. Добавить урок в курс")
    print("10. Изменить цену курса")
    print("11. Удалить курс")
    print("12. Записать студента на курс")
    print("13. Отметить урок пройденным")
    print("14. Удалить запись студента")
    print("15. Сохранить в JSON и XML")
    print("16. Загрузить из JSON")
    print("17. Загрузить из XML")
    print("0. Выход")


def main() -> None:
    manager = PlatformManager()
    fill_test_data(manager)

    while True:
        show_menu()
        cmd = input("Введите номер команды: ").strip()

        try:
            if cmd == "1":
                for u in manager.users.values():
                    print(f"ID {u.user_id}: {u.name} | роль: {u.get_role()} | {u.email}")

            elif cmd == "2":
                for c in manager.courses.values():
                    print(
                        f"Курс {c.course_id}: {c.title} ({c.price} руб., "
                        f"преп. ID {c.teacher_id}, всего {c.get_total_time()} мин.)"
                    )
                    for l in c.lessons:
                        print(f"   * Урок {l.lesson_id} [{l.get_type()}]: {l.title} ({l.minutes} мин.)")

            elif cmd == "3":
                for e in manager.enrollments.values():
                    print(
                        f"Запись {e.enroll_id}: студент {e.student_id} -> курс {e.course_id}, "
                        f"пройдено: {e.done_lessons}"
                    )

            elif cmd == "4":
                uid = int(input("ID студента: "))
                name = input("Имя: ")
                email = input("Email: ")
                level = input("Уровень: ")
                manager.add_user(Student(uid, name, email, level))
                print("Студент добавлен.")

            elif cmd == "5":
                uid = int(input("ID преподавателя: "))
                name = input("Имя: ")
                email = input("Email: ")
                subj = input("Предмет: ")
                rating = float(input("Рейтинг (0-5): "))
                manager.add_user(Instructor(uid, name, email, subj, rating))
                print("Преподаватель добавлен.")

            elif cmd == "6":
                uid = int(input("ID пользователя: "))
                name = input("Новое имя: ")
                manager.update_user_name(uid, name)
                print("Имя изменено.")

            elif cmd == "7":
                uid = int(input("ID пользователя: "))
                manager.delete_user(uid)
                print("Пользователь удален.")

            elif cmd == "8":
                cid = int(input("ID курса: "))
                title = input("Название: ")
                price = float(input("Цена: "))
                tid = int(input("ID преподавателя: "))
                manager.add_course(Course(cid, title, price, tid))
                print("Курс создан.")

            elif cmd == "9":
                cid = int(input("ID курса: "))
                kind = input("Тип (1 - видео, 2 - тест): ").strip()
                lid = int(input("ID урока: "))
                title = input("Название: ")
                mins = int(input("Длительность (мин): "))
                if kind == "1":
                    url = input("Ссылка: ")
                    manager.add_lesson(cid, VideoLesson(lid, title, mins, url))
                elif kind == "2":
                    q = int(input("Вопросов: "))
                    s = int(input("Проходной балл: "))
                    manager.add_lesson(cid, QuizLesson(lid, title, mins, q, s))
                else:
                    print("Неверный тип урока.")
                    continue
                print("Урок добавлен.")

            elif cmd == "10":
                cid = int(input("ID курса: "))
                price = float(input("Новая цена: "))
                manager.update_course_price(cid, price)
                print("Цена обновлена.")

            elif cmd == "11":
                cid = int(input("ID курса: "))
                manager.delete_course(cid)
                print("Курс удален.")

            elif cmd == "12":
                eid = int(input("ID записи: "))
                sid = int(input("ID студента: "))
                cid = int(input("ID курса: "))
                manager.add_enrollment(Enrollment(eid, sid, cid))
                print("Студент записан.")

            elif cmd == "13":
                eid = int(input("ID записи: "))
                lid = int(input("ID урока: "))
                manager.mark_lesson_done(eid, lid)
                print("Урок отмечен пройденным.")

            elif cmd == "14":
                eid = int(input("ID записи: "))
                manager.delete_enrollment(eid)
                print("Запись удалена.")

            elif cmd == "15":
                FileWorker.save_to_json("data.json", manager)
                FileWorker.save_to_xml("data.xml", manager)
                print("Сохранено в data.json и data.xml.")

            elif cmd == "16":
                FileWorker.load_from_json("data.json", manager)
                print("Загружено из data.json.")

            elif cmd == "17":
                FileWorker.load_from_xml("data.xml", manager)
                print("Загружено из data.xml.")

            elif cmd == "0":
                break

            else:
                print("Нет такой команды.")

        except PlatformError as e:
            print(f"Ошибка: {e}")
        except ValueError:
            print("Ошибка: нужно ввести число.")
        except (OSError, json.JSONDecodeError, ET.ParseError, KeyError) as e:
            print(f"Ошибка файла: {e}")


if __name__ == "__main__":
    main()
