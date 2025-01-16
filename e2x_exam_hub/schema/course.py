import os
from typing import Dict, List, Optional, Union

import yaml
from pydantic import Field

from .base import BaseCourse, Image, ModelWithCommands, Resources, Volume
from .exchange import ExchangeConfig
from .utils import load_user_list


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

    @classmethod
    def from_yaml_file(
        cls, base_path: str, course_name: str, semester_id: str, exam_period: str
    ) -> "StudentCourse":
        course_path = os.path.join(base_path, course_name)
        config_file = os.path.join(
            course_path,
            f"{course_name}.{semester_id}.{exam_period}.yaml",
        )
        user_file = os.path.join(
            course_path,
            f"{course_name}.{semester_id}.{exam_period}.csv",
        )
        with open(config_file, "r") as file:
            yaml_config = yaml.safe_load(file)
            return cls(
                name=course_name,
                semester_id=semester_id,
                exam_period=exam_period,
                course_members=load_user_list(user_file),
                **yaml_config,
            )

    def get_exchange_volume_mounts(
        self, volume: Volume, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        return self.exchange.get_volume_mounts(volume, self, username)

    def get_exchange_commands(self, nbgrader_config_file: str) -> List[str]:
        return self.exchange.get_commands(nbgrader_config_file)
