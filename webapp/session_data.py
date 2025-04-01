import dataclasses
from typing import TypedDict

from flask import session


class SessionData(TypedDict, total=False):
    """
    Enum class for session data

    Used to represent all the data stored in the session
    Should be accessed by session_data.get_session():

    ----------
    Attributes
    ----------
    """



def default_session_data() -> SessionData:
    """
    Returns the default session data
    :return: Default session data
    """
    return SessionData()


def get_session() -> 'SessionData':
    """
    Gets the session data from the flask session
    :return: Instance of the session data
    """
    return session
