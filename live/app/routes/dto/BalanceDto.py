from pydantic import BaseModel


class BalanceDto(BaseModel):
    userId: int
    value: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        self.userId = data["userId"]
        self.value = data["value"]
