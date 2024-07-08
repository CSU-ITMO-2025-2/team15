from pydantic import BaseModel


class TaskDto(BaseModel):
    id: int
    status: str
    datapath: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.id = data["id"]
        self.status = data["status"]
        self.datapath = data["datapath"]


class HistoryDto(BaseModel):
    id: int
    operation: str
    datetime: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.id = data["id"]
        self.operation = data["operation"]
        self.datetime = data["datetime"]
