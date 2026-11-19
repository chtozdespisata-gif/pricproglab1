import json
import xml.etree.ElementTree as ET
from exceptions import InputDataError
from models import (
    Course,
    Enrollment,
    Instructor,
    Lesson,
    QuizLesson,
    Student,
    User,
    VideoLesson,
)
from platform_manager import PlatformManager


class FileWorker:
    @staticmethod
    def save_to_json(path: str, manager: PlatformManager) -> None:
        courses_list = []
        for c in manager.courses.values():
            courses_list.append({
                "course_id": c.course_id,
                "title": c.title,
                "price": c.price,
                "teacher_id": c.teacher_id,
                "lessons": [lesson.to_dict() for lesson in c.lessons],
            })

        enrollments_list = []
        for e in manager.enrollments.values():
            enrollments_list.append({
                "enroll_id": e.enroll_id,
                "student_id": e.student_id,
                "course_id": e.course_id,
                "done_lessons": e.done_lessons,
            })

        data = {
            "users": [u.to_dict() for u in manager.users.values()],
            "courses": courses_list,
            "enrollments": enrollments_list,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_from_json(path: str, manager: PlatformManager) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        manager.reset()

        for u in data["users"]:
            role = u["role"]
            if role == "student":
                user: User = Student(int(u["user_id"]), u["name"], u["email"], u["level"])
            elif role == "instructor":
                user = Instructor(
                    int(u["user_id"]), u["name"], u["email"], u["subject"], float(u["rating"])
                )
            else:
                raise InputDataError("Неизвестная роль в файле")
            manager.add_user(user)

        for c in data["courses"]:
            lessons: list[Lesson] = []
            for l in c["lessons"]:
                if l["type"] == "video":
                    lessons.append(
                        VideoLesson(int(l["lesson_id"]), l["title"], int(l["minutes"]), l["url"], l["quality"])
                    )
                elif l["type"] == "quiz":
                    lessons.append(
                        QuizLesson(
                            int(l["lesson_id"]),
                            l["title"],
                            int(l["minutes"]),
                            int(l["questions"]),
                            int(l["pass_score"]),
                        )
                    )
                else:
                    raise InputDataError("Неизвестный тип урока в файле")

            course = Course(
                int(c["course_id"]), c["title"], float(c["price"]), int(c["teacher_id"]), lessons
            )
            manager.add_course(course)

        for e in data["enrollments"]:
            done = [int(x) for x in e["done_lessons"]]
            enroll = Enrollment(int(e["enroll_id"]), int(e["student_id"]), int(e["course_id"]), done)
            manager.add_enrollment(enroll)

    @staticmethod
    def save_to_xml(path: str, manager: PlatformManager) -> None:
        root = ET.Element("platform")

        users_tag = ET.SubElement(root, "users")
        for u in manager.users.values():
            u_tag = ET.SubElement(users_tag, "user", role=u.get_role())
            for k, v in u.to_dict().items():
                if k != "role":
                    ET.SubElement(u_tag, k).text = str(v)

        courses_tag = ET.SubElement(root, "courses")
        for c in manager.courses.values():
            c_tag = ET.SubElement(courses_tag, "course")
            ET.SubElement(c_tag, "course_id").text = str(c.course_id)
            ET.SubElement(c_tag, "title").text = c.title
            ET.SubElement(c_tag, "price").text = str(c.price)
            ET.SubElement(c_tag, "teacher_id").text = str(c.teacher_id)

            lessons_tag = ET.SubElement(c_tag, "lessons")
            for lesson in c.lessons:
                l_tag = ET.SubElement(lessons_tag, "lesson", type=lesson.get_type())
                for k, v in lesson.to_dict().items():
                    if k != "type":
                        ET.SubElement(l_tag, k).text = str(v)

        enrolls_tag = ET.SubElement(root, "enrollments")
        for e in manager.enrollments.values():
            e_tag = ET.SubElement(enrolls_tag, "enrollment")
            ET.SubElement(e_tag, "enroll_id").text = str(e.enroll_id)
            ET.SubElement(e_tag, "student_id").text = str(e.student_id)
            ET.SubElement(e_tag, "course_id").text = str(e.course_id)
            done_tag = ET.SubElement(e_tag, "done_lessons")
            for lid in e.done_lessons:
                ET.SubElement(done_tag, "lesson_id").text = str(lid)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def load_from_xml(path: str, manager: PlatformManager) -> None:
        tree = ET.parse(path)
        root = tree.getroot()
        manager.reset()

        for u_tag in root.findall("./users/user"):
            role = u_tag.attrib.get("role", "")
            uid = int(u_tag.findtext("user_id") or 0)
            name = u_tag.findtext("name") or ""
            email = u_tag.findtext("email") or ""

            if role == "student":
                level = u_tag.findtext("level") or "Beginner"
                manager.add_user(Student(uid, name, email, level))
            elif role == "instructor":
                subject = u_tag.findtext("subject") or ""
                rating = float(u_tag.findtext("rating") or 0)
                manager.add_user(Instructor(uid, name, email, subject, rating))
            else:
                raise InputDataError("Неизвестная роль в XML")

        for c_tag in root.findall("./courses/course"):
            lessons: list[Lesson] = []
            for l_tag in c_tag.findall("./lessons/lesson"):
                ltype = l_tag.attrib.get("type", "")
                lid = int(l_tag.findtext("lesson_id") or 0)
                title = l_tag.findtext("title") or ""
                minutes = int(l_tag.findtext("minutes") or 0)

                if ltype == "video":
                    url = l_tag.findtext("url") or ""
                    quality = l_tag.findtext("quality") or "1080p"
                    lessons.append(VideoLesson(lid, title, minutes, url, quality))
                elif ltype == "quiz":
                    q = int(l_tag.findtext("questions") or 0)
                    score = int(l_tag.findtext("pass_score") or 0)
                    lessons.append(QuizLesson(lid, title, minutes, q, score))
                else:
                    raise InputDataError("Неизвестный тип урока в XML")

            course = Course(
                int(c_tag.findtext("course_id") or 0),
                c_tag.findtext("title") or "",
                float(c_tag.findtext("price") or 0),
                int(c_tag.findtext("teacher_id") or 0),
                lessons,
            )
            manager.add_course(course)

        for e_tag in root.findall("./enrollments/enrollment"):
            done = [
                int(x.text)
                for x in e_tag.findall("./done_lessons/lesson_id")
                if x.text
            ]
            enroll = Enrollment(
                int(e_tag.findtext("enroll_id") or 0),
                int(e_tag.findtext("student_id") or 0),
                int(e_tag.findtext("course_id") or 0),
                done,
            )
            manager.add_enrollment(enroll)
