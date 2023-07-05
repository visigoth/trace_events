from ..field import Field


class EventMetaData(type):
    """
    Event metadata

    Field properties denote the data type, name, and a flag indicating whether they are required
    """

    @property
    def name_field(cls) -> Field:
        return Field(str, 'name')

    @property
    def event_type_field(cls) -> Field:
        return Field(str, 'ph')

    @property
    def category_field(cls) -> Field:
        return Field(str, 'cat', False, 'function')

    @property
    def process_id_field(cls) -> Field:
        return Field(int, 'pid', False, 0)

    @property
    def thread_id_field(cls) -> Field:
        return Field(int, 'tis', False, 0)
