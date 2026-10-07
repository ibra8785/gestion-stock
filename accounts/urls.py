# Importe la fonction permettant de définir les routes.
from django.urls import path

# Importe les vues d'authentification et de test des permissions.
from .views import UserLoginView, UserLogoutView, profile, test_delete_permission


# Définit les URLs de l'authentification.
urlpatterns = [
    # Route de connexion.
    path("login/", UserLoginView.as_view(), name="login"),

    # Route de déconnexion.
    path("logout/", UserLogoutView, name="logout"),

    # Route du profil.
    path("profile/", profile, name="profile"),

    # Route de test de la permission de suppression d'un produit.
    path(
        "permission-test/",
        test_delete_permission,
        name="permission_test",
    ),
]