class RepositoryInvalidDBPath(Exception):
    # if no path or incorrect path is given
    pass

class RepositoryRemoteAlreadyExists(Exception):
    pass

class RepositoryRemoteDoesNotExists(Exception):
    pass

class RepositoryRemotePushConflict(Exception):
    pass

class PackageManagerDBNotFound(Exception):
    pass

class PackageManagerDBAlreadyExists(Exception):
    pass

class PackageManagerInvalidDBPath(Exception):
    # if no path or incorrect path is given
    pass