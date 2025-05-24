from inspect import get_annotations
from annotated_types import Ge, Le
from typing import Literal, TypedDict, get_args, get_origin, Union, Annotated
from pydantic.fields import FieldInfo
from pydantic import BaseModel


class FieldData(BaseModel):
    name: str
    value: Union[str, int, float, tuple[str | int | float]]
    min_val: float | None = None
    max_val: float | None = None


class AnnotatedMetadata(TypedDict):
    ge: float | None
    le: float | None


def format_name(variable_name: str) -> str:
    return variable_name.replace("_", " ").title()


def get_members(tp: type) -> dict:
    return get_annotations(tp)


def extract_metadata(field_info: FieldInfo) -> AnnotatedMetadata:
    data: AnnotatedMetadata = {
        'ge': None,
        'le': None
    }

    for meta in field_info.metadata:
        if isinstance(meta, Ge):
            data['ge'] = float(meta.ge)
        elif isinstance(meta, Le):
            data['le'] = float(meta.le)

    return data


def is_optional(tp: type) -> bool:
    origin = get_origin(tp)

    # Optional is just Union[T,None]
    if origin is not Union:
        return False

    return type(None) in get_args(tp)


def map_primitive(name: str, tp: type) -> FieldData | None:
    data = FieldData(name=name, value="DEFAULT")

    if tp is int:
        data.value = 69

    elif tp is float:
        data.value = 420.69

    elif tp is str:
        data.value = "2137"

    elif get_origin(tp) is Literal:
        data.value = get_args(tp)

    elif is_optional(tp):
        inner_types = get_args(tp)

        if len(inner_types) != 2:
            raise Exception(f"Invalid inner optional types: {inner_types}")

        inner_type = next((x for x in inner_types if x != type(None)), None)

        if inner_type is None:
            raise Exception(f"Invalid inner optional types: {inner_types}. found: {inner_type}")

        prim = map_primitive(name, inner_type)

        if prim is None:
            return None

        data.value = prim.value

    elif get_origin(tp) is Annotated:

        args = get_args(tp)

        if len(args) == 0:
            print(f"Invalid Annotated type: {tp}")
            return None

        inner_type = get_args(tp)[0]

        if len(args) > 0:
            prim = map_primitive(name, inner_type)
            if prim is None:
                return None
            data.value = prim.value

        if len(args) > 1:
            for meta in args[1:]:
                if isinstance(meta, FieldInfo):
                    metadata = extract_metadata(meta)

                    data.max_val = metadata['le']
                    data.min_val = metadata['ge']


    else:
        return None

    return data


def map_members(tp) -> list[FieldData | str]:
    """ 
    Maps RAG config to data parseable by frontend

    """
    if not isinstance(tp, type):
        raise Exception(str(tp) + " is not a type")

    members_map = get_members(tp)

    fields: list[FieldData | str] = []

    for mname, minfo in members_map.items():

        formatted_name = format_name(mname)

        data = map_primitive(formatted_name, minfo)

        # Valid primitive type 
        if data is not None:
            fields.append(data)

        else:
            subfields = map_members(minfo)
            fields.append(formatted_name.capitalize())
            fields.extend(subfields)

    return fields


if __name__ == "__main__":
    class Test(BaseModel):
        test_str: str
        test_int: int
        test_int2: int
        test_float: float


    fields = Test.model_fields

    for m in map_members(Test):
        print(m)

    exit(-1)
