import os
from typing import Dict, List, Union

from traitlets import Unicode
from traitlets.config import Config, LoggingConfigurable

from .schema import BaseCourse, ServerConfig, StudentCourse


class ExamHub(LoggingConfigurable):
    config_base_path = Unicode(
        "/srv/jupyterhub/config", help="Base path for configuration files"
    ).tag(config=True)

    config_file_name = Unicode(
        "config-exam.yaml", help="Name of the configuration file"
    ).tag(config=True)

    server_config: ServerConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_config = ServerConfig.from_yaml_file(self.config_file_path)

    @property
    def config_file_path(self) -> str:
        """
        Constructs the full file path for a configuration file.

        Returns:
            str: The full path to the configuration file.
        """
        return os.path.join(self.config_base_path, self.config_file_name)

    def override_single_user_config(self, config: Config) -> None:
        """
        Overrides the single-user JupyterHub configuration with the image, CPU, and memory settings
        from the configuration file.

        Args:
            config (Config): The JupyterHub configuration object to be modified.
        Returns:
            None
        """
        config.KubeSpawner.image = self.server_config.image.full_image_name
        config.KubeSpawner.image_pull_policy = self.server_config.image.pullPolicy

        config.KubeSpawner.cpu_guarantee = self.server_config.resources.cpu_guarantee
        config.KubeSpawner.cpu_limit = self.server_config.resources.cpu_limit
        config.KubeSpawner.mem_guarantee = self.server_config.resources.mem_guarantee
        config.KubeSpawner.mem_limit = self.server_config.resources.mem_limit

    def get_hub_users(self) -> List[str]:
        """
        Returns a list of all users that are members of the courses configured in the JupyterHub.

        Returns:
            List[str]: A list of usernames.
        """
        users = []
        for course in self.server_config.nbgrader.student_courses:
            users.extend(course.course_members)
        return users

    def get_volume_mounts(
        self, course: BaseCourse, username: str
    ) -> List[Dict[str, Union[str, bool]]]:
        """
        Retrieve the volume mounts for a given course and username.

        Args:
            course (BaseCourse): The course for which to retrieve volume mounts.
            username (str): The username of the user for whom to retrieve volume mounts.

        Returns:
            List[Dict[str, Union[str, bool]]]: A list of dictionaries containing volume mount
            information.
        """
        return self.server_config.mounts.get_mounts(course, username)

    def get_user_courses(self, username: str) -> List[StudentCourse]:
        """
        Retrieve the list of courses for a given student.

        Args:
            username (str): The username of the student for whom to retrieve courses.

        Returns:
            List[StudentCourse]: A list of StudentCourse objects representing the courses of the
            student.
        """
        return self.server_config.nbgrader.get_user_courses(username)

    def get_server_commands(self) -> List[str]:
        """
        Retrieve the server commands for the JupyterHub.

        Returns:
            List[str]: A list of commands to be executed
        """
        return self.server_config.all_commands

    def get_course_commands(self, course: StudentCourse) -> List[str]:
        """
        Retrieve the course commands for a given course.

        Args:
            course (StudentCourse): The course for which to retrieve commands.

        Returns:
            List[str]: A list of commands to be executed
        """
        return course.all_commands
