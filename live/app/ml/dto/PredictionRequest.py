from pydantic import BaseModel


class WineParams(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

    class Config:
        from_attributes = True


class DataParams(BaseModel):
    id: int
    path: str
    datetime: str

    class Config:
        from_attributes = True
        coerce_numbers_to_str = True


class PredictionRequest(BaseModel):
    path2data: str
    namemodel: str
    task_id: int

    class Config:
        from_attributes = True
