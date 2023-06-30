import typing as t


class Field:
    """Description of an output field"""

    data_type: type
    name: str
    required: bool
    default: t.Any

    def __init__(self, data_type: type, name: str, required: bool = True, default: t.Any = None):
        self.data_type = data_type
        self.name = name
        self.required = required
        self.default = default

        if self.default is not None:
            assert isinstance(
                self.default, self.data_type), f'{self.name} default_value should be {data_type.__name__}, but is {type(self.default).__name__}'


def get_fields(data_type: type, data: dict):
    """Extracts data fields for the given data_type from a dictionary"""

    assert hasattr(
        data_type, 'fields'), f'type:{data_type.__name__} requires a \'fields\' property'

    def mapper(field: Field):
        value = data.get(field.name, None)

        if value is None:
            if field.required:
                raise KeyError(
                    f'Required field \'{field.name}\' of {data_type.__name__} is missing from json data')

            if field.default is not None:
                return field.default

            return None

        if isinstance(value, field.data_type):
            return value

        return field.data_type(value)

    return map(mapper, data_type.fields)
