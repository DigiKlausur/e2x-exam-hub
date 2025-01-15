import os

import yaml
from pydantic import Field

from .base import Image, ModelWithCommands, Resources
from .mounts import Mounts
from .nbgrader import NbGrader


class ServerConfig(ModelWithCommands):
    image: Image = Field(
        ...,
        description="Image settings",
    )
    resources: Resources = Field(
        ...,
        description="Resource settings",
    )
    nbgrader: NbGrader = Field(
        ...,
        description="NbGrader settings",
    )
    config_root: str = Field(
        ...,
        description="Root path for the configuration files",
    )
    mounts: Mounts = Field(
        ...,
        description="Mounts configuration",
    )

    @classmethod
    def from_yaml_file(cls, file_path: str):
        config_root = os.path.dirname(file_path)
        with open(file_path, "r") as file:
            yaml_config = yaml.safe_load(file)
            return cls(
                config_root=config_root,
                commands=yaml_config.get("commands", dict()),
                image=Image(**yaml_config["image"]),
                resources=Resources(**yaml_config["resources"]),
                nbgrader=NbGrader.from_dict(config_root, yaml_config["nbgrader"]),
                mounts=Mounts(**yaml_config["mounts"]),
            )
