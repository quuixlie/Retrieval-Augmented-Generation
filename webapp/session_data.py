import dataclasses
from typing import TypedDict

from flask import session


class SessionData(TypedDict, total=False):
    """
    Enum class for session data

    Used to represent all the data stored in the session
    Should be accessed by session_data.get_session():
    !!! Not to be confused with the applications active session and SessionModel !!!

    ----------
    Attributes
    ----------
    active_session_name : str
        The name of the active (SessionModel) session
    """

    active_session_name: str | None


def default_session_data() -> SessionData:
    """
    Returns the default session data
    :return: Default session data
    """
    return SessionData(active_session_name=None)


def get_session() -> 'SessionData':
    """
    Gets the session data from the flask session
    :return: Instance of the session data
    """
    return session
