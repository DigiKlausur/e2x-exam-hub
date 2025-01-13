from .schema.nbgrader import StudentCourse
from .schema.volume import HomeVolumeMount, SharedVolumeMount, TempVolumeMount, Volume


def get_volume_mounts(course: StudentCourse, username: str):
    volume_mounts = list()

    exchange_volume = Volume(name="disk3", sub_path="nbgrader/exchanges")

    volume_mounts.extend(course.get_exchange_volume_mounts(exchange_volume, username))

    volume_mounts.extend(
        SharedVolumeMount(name="disk3", sub_path="shares/exam").get_volume_mounts(
            course
        )
    )

    volume_mounts.extend(
        TempVolumeMount(name="disk2", sub_path="homes").get_volume_mounts(
            course, username
        )
    )

    volume_mounts.extend(
        HomeVolumeMount(name="disk2", sub_path="homes").get_volume_mounts(
            course, username
        )
    )

    return volume_mounts
