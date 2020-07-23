class UserNotFoundError(Exception):
    """
    The following user doesn't exist.
    """

class AccesDeniesError(Exception):
    """
    Access denied due to unmatching permissions.
    """

class ApiRequestError(Exception):
    """
    API request error.
    """

class CityNotFoundError(Exception):
    """
    City not found (weather command)
    """

exceptions = (UserNotFoundError, AccesDeniesError, ApiRequestError, CityNotFoundError)