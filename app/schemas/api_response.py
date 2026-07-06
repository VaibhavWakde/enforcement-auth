from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):

    status: str

    code: str

    message: str

    timestamp: datetime

    data: Any | None = None