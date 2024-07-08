from pydantic import BaseModel


class BalanceDto(BaseModel):
    id: int
    userId: int
    value: str

    def __init__(self, **data):
        super().__init__(**data)
        self.id = data["id"]
        self.userId = data["userId"]
        self.value = data["value"]
