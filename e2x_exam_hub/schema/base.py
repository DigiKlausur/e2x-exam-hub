from typing import Dict, List

from pydantic import BaseModel, Field


class ModelWithCommands(BaseModel):
    commands: Dict[str, List[str]] = Field(
        dict(),
        description="Commands to be executed. Split into sections",
    )

    @property
    def all_commands(self) -> List[str]:
        commands = []
        for section, command_list in self.commands.items():
            commands.extend([command for command in command_list])
        return commands


class Image(BaseModel):
    name: str = Field(
        ...,
        description="Name of the image",
    )
    tag: str = Field(
        ...,
        description="Tag of the image",
    )
    pullPolicy: str = Field(
        "IfNotPresent",
        description="Pull policy for the image. Default is 'IfNotPresent'",
        pattern="^(Always|IfNotPresent|Never)$",
    )

    @property
    def full_image_name(self):
        return f"{self.name}:{self.tag}"


class Resources(BaseModel):
    cpu_guarantee: float = Field(0.001, description="Guaranteed CPU resources")
    cpu_limit: float = Field(2.0, description="CPU resource limit")
    mem_guarantee: str = Field("1.0G", description="Guaranteed memory resources")
    mem_limit: str = Field("2.0G", description="Memory resource limit")


class BaseCourse(BaseModel):
    name: str = Field(
        ...,
        description="Name of the course",
    )
    semester_id: str = Field(
        ...,
        description="Semester of the course",
    )
    exam_period: str = Field(
        "PZ1",
        description="Exam period",
    )

    @property
    def course_id(self) -> str:
        return f"{self.name}-{self.semester_id}"
