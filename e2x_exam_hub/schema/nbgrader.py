import os
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .base import BaseCourse, Image, ModelWithCommands, Resources
from .utils import load_user_list
from .volume import Volume


class ExchangeConfig(BaseModel):
    personalized_feedback: bool = Field(
        True,
        description="Whether personalized feedback is enabled",
    )
    personalized_inbound: bool = Field(
        True,
        description="Whether personalized inbound is enabled",
    )
    personalized_outbound: bool = Field(
        False,
        description="Whether personalized outbound is enabled",
    )
    exchange_root: str = Field(
        "/srv/nbgrader/exchange", description="Root path for the exchange directory"
    )

    def _get_step_name(self, step: str) -> str:
        return f"personalized-{step}" if getattr(self, f"personalized_{step}") else step

    def _get_sub_path(
        self, volume: Volume, course: BaseCourse, username: str, step
    ) -> str:
        directory = self._get_step_name(step)
        path = os.path.join(
            volume.sub_path,
            course.name,
            course.course_id,
            directory,
        )
        if getattr(self, f"personalized_{step}"):
            path = os.path.join(path, username)
        return path

    def _get_mount_path(self, course: BaseCourse, username: str, step) -> str:
        directory = self._get_step_name(step)
        path = os.path.join(
            self.exchange_root,
            course.course_id,
            directory,
        )
        if getattr(self, f"personalized_{step}"):
            path = os.path.join(path, username)
        return path

    def get_volume_mounts(
        self, volume: Volume, course: BaseCourse, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        return [
            dict(
                name=volume.name,
                read_only=True,
                subPath=self._get_sub_path(volume, course, username, step),
                mountPath=self._get_mount_path(course, username, step),
            )
            for step in ["feedback", "inbound", "outbound"]
        ]

    def get_commands(self, nbgrader_config_file: str) -> List[str]:
        return [
            r"echo 'c.Exchange.personalized_feedback = {}' >> {}".format(
                self.personalized_feedback, nbgrader_config_file
            ),
            r"echo 'c.Exchange.personalized_inbound = {}' >> {}".format(
                self.personalized_inbound, nbgrader_config_file
            ),
            r"echo 'c.Exchange.personalized_outbound = {}' >> {}".format(
                self.personalized_outbound, nbgrader_config_file
            ),
        ]


class StudentCourse(BaseCourse, ModelWithCommands):
    course_members: List[str] = Field(
        list(),
        description="List of course members",
    )
    exchange: ExchangeConfig = Field(
        ExchangeConfig(),
        description="Exchange settings",
    )
    image: Optional[Image] = Field(
        None,
        description="Image settings",
    )
    resources: Optional[Resources] = Field(
        None,
        description="Resource settings",
    )

    def get_exchange_volume_mounts(
        self, volume: Volume, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        return self.exchange.get_volume_mounts(volume, self, username)

    def get_exchange_commands(self, nbgrader_config_file: str) -> List[str]:
        return self.exchange.get_commands(nbgrader_config_file)


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
        student_course_list = nbgrader_dict.get("student_course_list", dict())
        student_courses = []
        exam_course_dir = nbgrader_dict["exam_course_dir"]
        for course_name, semester_dict in student_course_list.items():
            for semester, course_dict in semester_dict.items():
                student_courses.append(
                    StudentCourse(
                        name=course_name,
                        semester_id=semester,
                        **course_dict,
                        course_members=load_user_list(
                            os.path.join(config_root, exam_course_dir),
                            course_name,
                            semester,
                        ),
                    )
                )
        return cls(
            exam_course_dir=exam_course_dir,
            student_courses=student_courses,
            commands=nbgrader_dict.get("commands", dict()),
        )

    def get_courses(self, username: str) -> List[StudentCourse]:
        return [
            course
            for course in self.student_courses
            if username in course.course_members
        ]
