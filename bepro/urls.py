from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
urlpatterns = [
    # url prefix api/v1
    path('api/v1/',include('api_server.urls'))
]
