from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
	id: int
	first_name: str
	username: str | None
	language_code: str
	is_admin: bool
