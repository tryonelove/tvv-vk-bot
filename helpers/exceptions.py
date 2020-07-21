class UserNotFoundError(Exception):
    """
    The following user doesn't exist.
    """

class AccesDenies(Exception):
    """
    Access denied due to unmatching permissions.
    """

class APIRequestError(Exception):
    """
    API request error.
    """

class CityNotFoundError(Exception):
    """
    City not found (weather command)
    """