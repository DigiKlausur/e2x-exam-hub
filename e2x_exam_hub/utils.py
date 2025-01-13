import os

from traitlets.config import Config

from .config import load_config


def get_config_file_path(config_mount: str, config_file: str) -> str:
    """
    Constructs the full file path for a configuration file.

    Args:
        config_mount (str): The base directory where the configuration files are mounted.
        config_file (str): The name of the configuration file.

    Returns:
        str: The full path to the configuration file.
    """
    return os.path.join(config_mount, config_file)


def override_singleuser_config(config: Config, path_to_config_file: str) -> None:
    """
    Overrides the single-user JupyterHub configuration with settings from a specified configuration
    file.

    Performs the following operations:
      - Sets the image for the JupyterHub server.
      - Sets the image pull policy.
      - Sets the CPU and memory guarantees and limits for the JupyterHub server.

    Args:
        config (Config): The JupyterHub configuration object to be modified.
        path_to_config_file (str): The path to the configuration file containing the new settings.
    Returns:
        None
    """

    server_config = load_config(path_to_config_file)

    config.KubeSpawner.image = server_config.image.full_image_name
    config.KubeSpawner.image_pull_policy = server_config.image.pull_policy

    config.KubeSpawner.cpu_guarantee = server_config.resources.cpu_guarantee
    config.KubeSpawner.cpu_limit = server_config.resources.cpu_limit
    config.KubeSpawner.mem_guarantee = server_config.resources.mem_guarantee
    config.KubeSpawner.mem_limit = server_config.resources.mem_limit
