class NoAdminPermissions(Exception):
    """
    Необходимая роль: администратор
    """
    pass

class NoDonorPermissions(Exception):
    """
    Необходимая роль: донатер
    """
    pass

class NoPrivilegesPermissions(Exception):
    """
    Необходимая роль: донатер или админ
    """
    pass

class ArgumentError(Exception):
    """
    Проверьте правильность аргументов
    """
    pass

class ApiError(Exception):
    """
    Ошибка при запросе к апи
    """
    pass

class CustomException(Exception):
    pass
    
