# Importe les vues d'authentification intégrées à Django.
from django.contrib.auth.views import LoginView

# Importe la fonction permettant de déconnecter l'utilisateur.
from django.contrib.auth import logout

# Importe les décorateurs qui protègent les vues.
from django.contrib.auth.decorators import login_required, permission_required

# Importe redirect et render pour gérer les redirections et les templates.
from django.shortcuts import redirect, render


# Vue de connexion des utilisateurs.
class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    # Redirige l'utilisateur vers son profil après une connexion réussie.
    next_page = "/accounts/profile/"


# Vue personnalisée de déconnexion.
def UserLogoutView(request):
    # Déconnecte l'utilisateur actuellement connecté.
    logout(request)

    # Redirige immédiatement vers la page de connexion.
    return redirect("login")


# Page du profil accessible uniquement aux utilisateurs connectés.
@login_required
def profile(request):
    return render(request, "accounts/profile.html")


# Page accessible uniquement aux utilisateurs ayant la permission de supprimer un produit.
@login_required
@permission_required("stock.delete_product", raise_exception=True)
def test_delete_permission(request):
    return render(request, "accounts/permission_test.html")