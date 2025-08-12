# Base ServiceException class
class ServiceException(Exception):
    pass

class BadRequestException(ServiceException):
    pass

class UnauthorizedException(ServiceException):
    pass