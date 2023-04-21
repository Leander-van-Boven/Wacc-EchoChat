from humps.main import camelize
from pydantic import BaseModel


def to_camelcase(string):
    """
    Convert a string to camelCase (unless the string starts with '_').
    :param string: The string to convert
    :return: The converted string
    """
    if string.startswith('_'):
        return string
    return camelize(string)


class BaseSchema(BaseModel):
    """
    Base schema for all schemas.
    Will convert all snake_case fields to camelCase, and vice versa.
    """
    class Config:
        orm_mode = True
        alias_generator = to_camelcase
        allow_population_by_field_name = True
