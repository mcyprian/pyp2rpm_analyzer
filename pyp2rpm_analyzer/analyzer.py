import sys
import urllib
import gzip
import copr
import re
import pprint
import tempfile

from pyp2rpm_analyzer import settings

url_template = settings.PROJECT_URL + '/00{0}-{1}/{2}.log.gz'

ROOT_PATTERNS = {
    'Missing package': b'No Package found for',
    'Missing dependency': b'No matching package to install'
}

BUILD_PATTERNS = {
    'Missing extension': b'Could not import extension',
    'Sphinx': b'Running Sphinx',
    'Unpackaged files': b'Installed (but unpackaged) file(s) found',
    'File not found': b'File not found: ',
    'Python traceback': b'Traceback (most recent call last)',
    'SyntaxError': b'SyntaxError:',
    'TestsFailure': b'Bad exit status from .* \(\%check\)',
    'BuildFailure': b'Bad exit status from .* \(\%build\)'
}


def builds_iter():
    """Iterator over all builds in copr project."""
    cl = copr.create_client2_from_file_config()
    pypi_project = cl.projects.get_list(name=settings.COPR_PROJECT, limit=3)[0]
    builds = pypi_project.get_builds()

    for build in builds:
        yield (build.package_name, url_template.format(
            build.id, build.package_name, "build"),
               url_template.format(build.id, build.package_name, "root"))


def failed_builds_iter():
    """Iterator over all failed builds in copr project."""
    cl = copr.create_client2_from_file_config()
    pypi_project = cl.projects.get_list(name=settings.COPR_PROJECT, limit=3)[0]
    builds = pypi_project.get_builds()

    for build in builds:
        if build.state == 'failed':
            yield (build.package_name, url_template.format(
                build.id, build.package_name, "build"),
                   url_template.format(build.id, build.package_name, "root"))


def extract_file_content(msg, filename, fo=None):
    with gzip.open(filename, 'r') as fi:
        tail = fi.readlines()[-40:]
        if not fo:
            return tail
        fo.write(msg)
        for line in tail:
            fo.write(line.decode())


def find_match(log, pattern_dict, fo):
    """Search for pattern match in given log ."""
    for name, pattern in pattern_dict.items():
        for line in log:
            if re.search(pattern, line):
                return name

    for line in log:
        fo.write(line.decode())
    return "Other error"


def analyse_builds():
    """Analysis of build and root logs. Check if part of log matches
    one of the frequent error patterns, mark build as 'Other error' otherwise.
    """
    issues_summary = {**BUILD_PATTERNS, **ROOT_PATTERNS}
    for key in issues_summary:
        issues_summary[key] = [0, []]
    issues_summary['Other error'] = [0, []]

    with tempfile.TemporaryDirectory() as tempdir:
        with open("/tmp/pyp2rpm_analysis.log", "w") as fo:
            for name, build_url, root_url in failed_builds_iter():
                if name is None:
                    continue
                build_name = tempdir + name + 'build.gz'
                root_name = tempdir + name + 'root.gz'
                try:
                    urllib.request.urlretrieve(build_url, build_name)
                    urllib.request.urlretrieve(root_url, root_name)
                except urllib.error.HTTPError:
                    sys.stderr.write(
                        "Failed to download logs for package {0}\n".format(name))
                    continue
                fo.write("\n#*#=============================== " +
                         name + " ===============================\n")
                try:
                    root_log = extract_file_content("ROOTLOG:\n\n", root_name)
                    build_log = extract_file_content(
                        "\nBUILDLOG:\n\n", build_name)
                except FileNotFoundError as e:
                    sys.stderr.write(e)
                    continue
                if len(build_log) < 10:
                    issue = find_match(root_log, ROOT_PATTERNS, fo)
                    issues_summary[issue][0] += 1
                    issues_summary[issue][1].append(name)
                    print("{0}: {1}".format(name, issue))
                else:
                    issue = find_match(build_log, BUILD_PATTERNS, fo)
                    issues_summary[issue][0] += 1
                    issues_summary[issue][1].append(name)
                    print("{0}: {1}".format(name, issue))
    pprint.pprint(issues_summary)
    print("Total: {} packages".format(len(list(failed_builds_iter()))))
