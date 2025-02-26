import os
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .base import BaseCourse, Volume
from .course import StudentCourse


class Mount(BaseModel):
    """
    Mount represents a configuration for a mount point in a system.

    Attributes:
        name (str): Name of the mount.
        readOnly (bool): Whether the mount is read-only. Defaults to True.
        subPath (str): Sub-path for the mount.
        mountPath (str): Mount path for the mount.
    """

    name: str = Field(
        ...,
        description="Name of the mount",
    )
    readOnly: bool = Field(
        True,
        description="Whether the mount is read-only",
    )
    subPath: str = Field(
        ...,
        description="Sub-path for the mount",
    )
    mountPath: str = Field(
        ...,
        description="Mount path for the mount",
    )


class Mounts(BaseModel):
    """
    Mounts schema for managing volume mounts in an exam hub environment.

    Attributes:
        exchange (Volume): Volume for the exchange directory.
        shared (Volume): Volume for the shared directory.
        temp (Volume): Volume for the temporary directory.
        home (Volume): Volume for the home directory.

    Methods:
        _get_temp_mount(course: BaseCourse, username: str) -> Mount:
            Returns a Mount object for the temporary directory specific to a course and user.

        _get_share_mounts(course: BaseCourse) -> List[Mount]:
            Returns the Mount objects for the shared directory specific to a course.

        _get_home_mount(course: BaseCourse, username: str) -> Mount:
            Returns a Mount object for the home directory specific to a course and user.

        _get_exchange_mounts(course: BaseCourse, username: str) -> List[Mount]:
            Returns a list of Mount objects for the exchange directory specific to a course
            and user.

        get_mounts(course: BaseCourse, username: str) -> List[Mount]:
            Returns a list of all Mount objects (temp, shared, home, exchange) specific to a course
            and user.
    """

    exchange: Volume = Field(
        ...,
        description="Volume for the exchange directory",
    )
    share: Optional[Volume] = Field(
        None,
        description="Volume for the shared directory",
    )
    temp: Volume = Field(
        ...,
        description="Volume for the temporary directory",
    )
    home: Volume = Field(
        ...,
        description="Volume for the home directory",
    )

    def _get_temp_mount(self, course: BaseCourse, username: str) -> Mount:
        """
        Creates a temporary mount for a given course and user.

        Args:
            course (BaseCourse): The course for which the temporary mount is created.
            username (str): The username of the user for whom the temporary mount is created.

        Returns:
            Mount: A Mount object configured with the temporary mount settings.
        """
        return Mount(
            name=self.temp.name,
            readOnly=False,
            subPath=os.path.join(
                self.temp.subPath,
                "exam",
                f"{course.semester_id}-{course.exam_period}",
                f"{course.name}-{username}",
                ".tmp",
            ),
            mountPath="/tmp",
        )

    def _get_share_mounts(self, course: BaseCourse) -> List[Mount]:
        """
        Get the shared mount configuration for a given course.

        Args:
            course (BaseCourse): The course for which to get the shared mount.

        Returns:
            List[Mount]: The mount configurations for the shared directory of the course.
        """
        if self.share is None:
            return []
        public_share_mount = Mount(
            name=self.share.name,
            readOnly=True,
            subPath=os.path.join(self.share.subPath, "public"),
            mountPath=os.path.join("/srv/shares", "public"),
        )
        course_share_mount = Mount(
            name=self.share.name,
            readOnly=True,
            subPath=os.path.join(self.share.subPath, "courses", course.name),
            mountPath=os.path.join("/srv/shares", course.name),
        )
        return [public_share_mount, course_share_mount]

    def _get_home_mount(self, course: BaseCourse, username: str) -> Mount:
        """
        Generates a Mount object for the home directory of a user in a specific course.

        Args:
            course (BaseCourse): The course object containing course details.
            username (str): The username of the student.

        Returns:
            Mount: A Mount object configured for the user's home directory.
        """
        return Mount(
            name=self.home.name,
            readOnly=False,
            subPath=os.path.join(
                self.home.subPath,
                "exam",
                f"{course.semester_id}-{course.exam_period}",
                f"{course.name}-{username}",
                "home",
            ),
            mountPath="/home/jovyan",
        )

    def _get_exchange_mounts(self, course: StudentCourse, username: str) -> List[Mount]:
        """
        Retrieve the exchange volume mounts for a given course and user.

        Args:
            course (BaseCourse): The course object containing the exchange volume mounts.
            username (str): The username of the user for whom the mounts are being retrieved.

        Returns:
            List[Mount]: A list of Mount objects representing the exchange volume mounts.
        """
        return course.get_exchange_volume_mounts(self.exchange, username)

    def get_mounts(
        self, course: StudentCourse, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        """
        Retrieve a list of mounts for a given course and user.

        This method generates a list of mounts by combining temporary, shared, home,
        and exchange mounts for the specified course and username.

        Args:
            course (StudentCourse): The course for which mounts are being retrieved.
            username (str): The username of the user for whom mounts are being retrieved.

        Returns:
            List[Mount]: A list of Mount objects representing the various mounts for the course
            and user.
        """
        mounts = list()

        mounts.append(self._get_temp_mount(course, username).model_dump())
        for mount in self._get_share_mounts(course):
            mounts.append(mount.model_dump())
        mounts.append(self._get_home_mount(course, username).model_dump())

        mounts.extend(self._get_exchange_mounts(course, username))

        return mounts
