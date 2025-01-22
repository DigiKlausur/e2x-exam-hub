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

    def _get_subPath(
        self, volume: Volume, course: BaseCourse, username: str, step
    ) -> str:
        directory = self._get_step_name(step)
        path = os.path.join(
            volume.subPath,
            course.name,
            course.course_id,
            directory,
        )
        if getattr(self, f"personalized_{step}"):
            path = os.path.join(path, username)
        return path

    def _get_mountPath(self, course: BaseCourse, username: str, step) -> str:
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
        mounts = [
            dict(
                name=volume.name,
                readOnly=True,
                subPath=self._get_subPath(volume, course, username, step),
                mountPath=self._get_mountPath(course, username, step),
            )
            for step in ["feedback", "outbound"]
        ]
        # Inbound is always read-write for the student
        mounts.append(
            dict(
                name=volume.name,
                readOnly=False,
                subPath=self._get_subPath(volume, course, username, "inbound"),
                mountPath=self._get_mountPath(course, username, "inbound"),
            )
        )
        return mounts

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
