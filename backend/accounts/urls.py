
from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    AuthStatusAPIView,
    profile_view,
    permission_test_view,
)

urlpatterns = [
    # Connexion et déconnexion.
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView, name="logout"),

    # Vérification de la session Django depuis React.
    path(
        "auth-status/",
        AuthStatusAPIView.as_view(),
        name="auth-status",
    ),

    # Pages du compte utilisateur.
    path("profile/", profile_view, name="profile"),
    path(
        "permission-test/",
        permission_test_view,
        name="permission-test",
    ),
]
