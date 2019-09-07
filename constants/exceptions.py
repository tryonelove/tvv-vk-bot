class NoAdminPermissions(Exception):
    pass

class NoDonorPermissions(Exception):
    pass

class NoPrivilegesPermissions(Exception):
    pass

class ArgumentError(Exception):
    pass

class ApiError(Exception):
    pass

class CustomException(Exception):
    pass
    
class ScoreMessageNotFound(Exception):
    pass

class dbUserNotFound(Exception):
    pass

class NoEditPermissions(Exception):
    pass

class UserNotFound(Exception):
    pass