from enum import Enum


class SessionStatus(Enum):
    IN_PROGRESS = 0
    LOGGED_OUT = 1
    TIMED_OUT = 2
    FORCED_LOGOUT = 3
    LOGOUT_IN_PROGRESS = 4
    INCORRECT_PASSWORD = 5
    INVALID_LOGIN = 6
    SYSTEM_ERROR = 7
    USER_NOT_ACTIVE = 8
    USER_UNAPPROVED = 9
    ACCOUNT_EXPIRED = 10
    USER_EXISTS = 11