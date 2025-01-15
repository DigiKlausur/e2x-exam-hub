import os
from typing import Dict, List

from pydantic import BaseModel, Field

from .course import StudentCourse


class SemesterConfig(BaseModel):
    semester: str = Field(
        ...,
        description="Semester ID",
    )
    exam_period: str = Field(
        ...,
        description="Exam period",
    )


class ActiveCourseConfig(BaseModel):
    semesters: List[SemesterConfig] = Field(
        ...,
        description="List of semesters",
    )


class ActiveStudentCourses(BaseModel):
    courses: Dict[str, ActiveCourseConfig] = Field(
        ...,
        description="List of courses",
    )


class NbGrader(BaseModel):
    exam_course_dir: str = Field(
        ...,
        description="Path to where exam user lists are stored",
    )
    exchange_root: str = Field(
        "/srv/nbgrader/exchange",
        description="Root path for the exchange directory",
    )
    student_courses: List[StudentCourse] = Field(
        [],
        description="List of courses",
    )

    @classmethod
    def from_dict(cls, config_root: str, nbgrader_dict: dict):
        active_student_courses = ActiveStudentCourses(
            courses=nbgrader_dict.get("active_student_courses", dict())
        )
        exam_course_dir = nbgrader_dict["exam_course_dir"]
        student_courses = []
        for course_name, active_course_config in active_student_courses.courses.items():
            for semester_config in active_course_config.semesters:
                student_courses.append(
                    StudentCourse.from_yaml_file(
                        os.path.join(config_root, exam_course_dir),
                        course_name,
                        semester_config.semester,
                        semester_config.exam_period,
                    )
                )
        return cls(
            exam_course_dir=exam_course_dir,
            student_courses=student_courses,
            commands=nbgrader_dict.get("commands", dict()),
        )

    def get_user_courses(self, username: str) -> List[StudentCourse]:
        return [
            course
            for course in self.student_courses
            if username in course.course_members
        ]
