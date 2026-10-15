
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class UserLoginView(LoginView):
    # Chemin réel du formulaire de connexion.
    template_name = "accounts/login.html"

    # Destination par défaut après une connexion réussie.
    next_page = "http://localhost:5173/"

    # Autorise les redirections vers React en développement.
    success_url_allowed_hosts = {
        "localhost:5173",
        "127.0.0.1:5173",
    }


def UserLogoutView(request):
    # Ferme la session de l'utilisateur.
    logout(request)

    # Retourne au formulaire de connexion après la déconnexion.
    return redirect("login")


def profile_view(request):
    # Affiche le profil uniquement aux utilisateurs connectés.
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "accounts/profile.html")


def permission_test_view(request):
    # Vérifie que la protection des pages fonctionne.
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "accounts/permission_test.html")


class AuthStatusAPIView(APIView):
    # Cette route doit fonctionner même sans connexion.
    permission_classes = [AllowAny]

    def get(self, request):
        # Indique si une session utilisateur est active.
        is_authenticated = request.user.is_authenticated

        return Response({
            "is_authenticated": is_authenticated,
            "username": (
                request.user.username if is_authenticated else None
            ),
        })
