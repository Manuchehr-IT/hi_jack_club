from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def api_root(request):
	return JsonResponse({
		"message": "Telegram Mini App API is working!",
		"endpoints": {
			"admin": "/admin/",
			"api_auth": "/api-auth/",
			"swagger": "/api/schema/swagger/",
			"redoc": "/api/schema/redoc/",
			"schema": "/api/schema/"
		}
	})

urlpatterns = [
	path("api/", api_root, name="api-root"),

	path("admin/", admin.site.urls),
	path("ckeditor5/", include("django_ckeditor_5.urls")),

	# Подключаем URLs из приложений
	path("api/", include("apps.users.api.urls")),
	path("api/", include("apps.tournaments.api.urls")),
	path("api/", include("apps.faq.api.urls")),
	path("api/", include("apps.about_club.api.urls")),
	path("api/", include("apps.social_network.api.urls")),

	path("api-auth/", include("rest_framework.urls")),
	path("api/health/", lambda request: JsonResponse({"message": "ok", "status": "health"})),

	# Документация
	path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
	path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
