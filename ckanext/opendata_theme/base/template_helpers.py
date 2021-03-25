from packaging.version import Version, InvalidVersion


def version_builder(text_version):
    return Version(text_version)
