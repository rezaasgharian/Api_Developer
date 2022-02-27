from django.urls import path,include
from .views import testAPIView
urlpatterns = [
    # the url that runs the test file /api/v1/tests
    path('tests',testAPIView.as_view(),name='test')
]
