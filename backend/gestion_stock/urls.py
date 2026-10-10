"""
URL configuration for gestion_stock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Importe l'administration Django.
from django.contrib import admin

# Importe path pour définir les URLs et include pour connecter les applications.
from django.urls import include, path


# Définit les routes principales de notre projet.
urlpatterns = [
    # Conserve l'accès à l'administration Django.
    path("admin/", admin.site.urls),

    # Connecte les URLs de l'application stock sous le préfixe /api/.
    path("api/", include("stock.urls")),

    # Connecte les URLs de l'authentification sous le préfixe /accounts/.
    path("accounts/", include("accounts.urls")),
]