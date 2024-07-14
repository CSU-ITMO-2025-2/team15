from typing import Union

from pydantic import BaseModel


class TaskDto(BaseModel):
    id: int
    status: str
    datapath: str
    predicted_value: Union[str, None] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.id = data["id"]
        self.status = data["status"]
        self.datapath = data["datapath"]
        self.predicted_value = data["predicted_value"]

    class Config:
        from_attributes = True


class HistoryDto(BaseModel):
    id: int
    operation: str
    datetime: str

    def __init__(self, **data):
        super().__init__(**data)
        self.id = data["id"]
        self.operation = data["operation"]
        self.datetime = data["datetime"]
