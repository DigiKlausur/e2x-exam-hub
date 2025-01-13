import os
from typing import Dict, List, Union

from pydantic import BaseModel, Field

from .base import BaseCourse


class Volume(BaseModel):
    name: str = Field(
        ...,
        description="Name of the volume",
    )
    sub_path: str = Field(
        ...,
        description="Sub-path for the volume",
    )


class SharedVolumeMount(Volume):
    base_path: str = Field(
        "/srv/shares",
        description="Base mount path for shared volumes",
    )

    def get_volume_mounts(
        self, course: BaseCourse
    ) -> List[Dict[str, Union[str, bool]]]:
        public_share_mount = dict(
            name=self.name,
            read_only=True,
            subPath=os.path.join(self.sub_path, "public"),
            mountPath=os.path.join(self.base_path, "public"),
        )
        course_share_mount = dict(
            name=self.name,
            read_only=True,
            subPath=os.path.join(self.sub_path, "courses", course.name),
            mountPath=os.path.join(self.base_path, course.name),
        )
        return [public_share_mount, course_share_mount]


class TempVolumeMount(Volume):
    def get_volume_mounts(
        self, course: BaseCourse, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        return [
            dict(
                name=self.name,
                read_only=False,
                subPath=os.path.join(
                    self.sub_path,
                    "exam",
                    f"{course.semester_id}-{course.exam_period}",
                    f"{course.name}-{username}",
                    ".tmp",
                ),
                mountPath="/tmp",
            )
        ]


class HomeVolumeMount(Volume):
    def get_volume_mounts(
        self, course: BaseCourse, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        return [
            dict(
                name=self.name,
                read_only=False,
                subPath=os.path.join(
                    self.sub_path,
                    "exam",
                    f"{course.semester_id}-{course.exam_period}",
                    f"{course.name}-{username}",
                    "home",
                ),
                mountPath="/home/jovyan",
            )
        ]
