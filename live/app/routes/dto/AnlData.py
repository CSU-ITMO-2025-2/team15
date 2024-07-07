from pydantic import BaseModel


class WineInput(BaseModel):
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


class SuccessResponse(BaseModel):
    message: str

    def __init__(self, message: str, **data: Any):
        super().__init__(**data)
        self.message = message


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.access_token = data['access_token']
        self.token_type = data['token_type']
