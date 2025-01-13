from typing import Dict, List, Union


def deduplicate_mounts(
    mounts: List[Dict[str, Union[str, bool]]]
) -> List[Dict[str, Union[str, bool]]]:
    existing_mount_paths = set()
    deduplicated_mounts = []
    for mount in mounts:
        if mount["mountPath"] in existing_mount_paths:
            continue
        else:
            existing_mount_paths.add(mount["mountPath"])
            deduplicated_mounts.append(mount)
    return deduplicated_mounts
