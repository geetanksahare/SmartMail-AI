from pydantic import BaseModel


class TestEmailResponse(BaseModel):
    message: str
    message_id: str