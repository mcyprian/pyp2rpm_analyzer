PYP2RPM_BIN = '/home/mcyprian/Codes/devel/pyp2rpm/mybin.py'
FLAGS = ''
COPR_PROJECT = 'pypi_builds3'
COPR_LOGIN = 'mcyprian'
CHROOTS = ['fedora-26-x86_64']
SAVE_PATH = '/tmp/srpms'
PROJECT_URL = "https://copr-be.cloud.fedoraproject.org/results/{0}/{1}/{2}".format(
    COPR_LOGIN, COPR_PROJECT, CHROOTS[0])
