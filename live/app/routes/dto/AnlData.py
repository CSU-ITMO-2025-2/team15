from pydantic import BaseModel

class SuccessResponse(BaseModel):
    message: str

    def __init__(self, message: str, **data):
        super().__init__(**data)
        self.message = message


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    def __init__(self, **data):
        super().__init__(**data)
        self.access_token = data['access_token']
        self.token_type = data['token_type']
