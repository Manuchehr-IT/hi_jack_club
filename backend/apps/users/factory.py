from .services import UserService

def create_user_service() -> UserService:
	return UserService()
