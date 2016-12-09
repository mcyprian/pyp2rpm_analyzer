import copr
import os

from pyp2rpm_analyzer import settings


def create_builds():
    """Push builds of all SRPMS from SAVE_PATH to copr project.
    Project is created if it doesn't exists."""
    cl = copr.create_client2_from_file_config()
    try:
        pypi_project = cl.projects.get_list(name=settings.COPR_PROJECT,
                                            limit=3)[0]
    except IndexError:
        pypi_project = cl.projects.create(name=settings.COPR_PROJECT,
                                          chroots=settings.CHROOTS,
                                          owner=settings.COPR_LOGIN)

    files_to_build = [pkg for pkg in os.listdir(settings.SAVE_PATH)
                      if pkg.endswith('.src.rpm')]
    print("Submited builds:")
    for f in files_to_build:
        print(f)
        pypi_project.create_build_from_file(settings.SAVE_PATH + f)

if __name__ == '__main__':
    create_builds()
