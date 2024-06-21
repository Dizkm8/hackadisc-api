"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api_auth.views import MyTokenObtainPairView
from api_system.views import WorkerListView, InterventionDocumentsView, get_worker_by_rut, get_workers_by_competence, create_intervention, get_all_evaluations

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/workers/", WorkerListView.as_view()),
    path('api/worker/<str:rut>/', get_worker_by_rut, name='get_worker_by_rut'),
    path("api/interventions/<int:id>/documents/", InterventionDocumentsView.as_view()),
    path('api/workers/competence/<int:competence_id>/', get_workers_by_competence, name='get_workers_by_competence'),
    path('api/create_intervention/', create_intervention, name='create_intervention'),
    path('api/evaluations/', get_all_evaluations, name='get_all_evaluations'),

]
