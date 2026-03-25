from .services import TournamentService
from apps.iiko.factory import create_iiko_service

def create_tournament_service():
	return TournamentService(iiko_service=create_iiko_service())
