"""schemas untuk endpoint telkomsel."""

from pydantic import BaseModel, Field


class TselConfig(BaseModel):
    """shared setup for telkomsel."""

    model_config = {
        "from_attributes": True,
    }

    username: str = Field(
        description="Username API/Account Telkomsel, harus matches dengan data di secret/telkomsel.toml",
        examples=["user1", "user2"],
    )
    to: str = Field(
        ..., description="Recipient number", examples=["08123456789", "08234567890"]
    )
