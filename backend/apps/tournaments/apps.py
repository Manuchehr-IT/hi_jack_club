from django.apps import AppConfig

class TournamentConfig(AppConfig):
	name = "apps.tournaments"

	def ready(self):
		import apps.tournaments.signals
