import os
from typing import Dict, List, Union

from pydantic import BaseModel, Field

from .base import BaseCourse, Volume


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
