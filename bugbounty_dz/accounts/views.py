from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from .models import UserHacker
import hashlib
import os
import binascii
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import UserHacker, Enterprise
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class Home(View):
    def get(self, request):
        return render(request, "home.html")


class HackerLoginView(View):
    def get(self, request):
        return render(request, "hackerlogin.html")

    def post(self, request):
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')

        try:
            hacker = UserHacker.objects.get(email=email)

            # 🔐 Vérification avec Django
            if not check_password(mot_de_passe, hacker.mot_de_passe_hash):
                error = "Mot de passe incorrect"

            elif hacker.statut != 'actif':
                error = f"Votre compte est {hacker.statut}. Contactez le support."

            elif not hacker.verifiee:
                error = "Votre compte n'est pas encore vérifié."

            else:
                # Connexion réussie
                request.session['hacker_id'] = hacker.id
                request.session['hacker_email'] = hacker.email
                request.session['hacker_nom'] = f"{hacker.prenom} {hacker.nom}"
                request.session['user_type'] = 'hacker'
                request.session['logged_in'] = True

                hacker.date_derniere_connexion = timezone.now()
                hacker.save()

                return redirect('hacker_home')

        except UserHacker.DoesNotExist:
            error = "Aucun compte trouvé avec cet email"

        return render(request, "hackerlogin.html", {
            "error": error
        })
class HackerRegisterView(View):
    def get(self, request):
        return render(request, "hackerregister.html")

    def post(self, request):
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        date_naissance = request.POST.get('date_naissance')
        adresse = request.POST.get('adresse')
        cni_numero = request.POST.get('cni_numero')
        mot_de_passe = request.POST.get('mot_de_passe')
        mot_de_passe_confirm = request.POST.get('mot_de_passe_confirm')
        cni_image_file = request.FILES.get('cni_image')

        # Vérification des mots de passe
        if mot_de_passe != mot_de_passe_confirm:
            return render(request, "hackerregister.html", {
                "error": "Les mots de passe ne correspondent pas"
            })

        # Vérifications d'unicité
        if UserHacker.objects.filter(email=email).exists():
            return render(request, "hackerregister.html", {
                "error": "Un compte avec cet email existe déjà"
            })

        if UserHacker.objects.filter(telephone=telephone).exists():
            return render(request, "hackerregister.html", {
                "error": "Un compte avec ce numéro de téléphone existe déjà"
            })

        if UserHacker.objects.filter(cni_numero=cni_numero).exists():
            return render(request, "hackerregister.html", {
                "error": "Ce numéro de CIN est déjà utilisé"
            })

        # Sauvegarde de l'image CIN
        cni_image_path = None
        if cni_image_file:
            fs = FileSystemStorage(location='media/cni')
            filename = fs.save(cni_image_file.name, cni_image_file)
            cni_image_path = f"cni/{filename}"

        # 🔐 Hash du mot de passe avec Django
        mot_de_passe_hash = make_password(mot_de_passe)

        # Création du hacker
        hacker = UserHacker.objects.create(
            prenom=prenom,
            nom=nom,
            email=email,
            telephone=telephone,
            date_naissance=date_naissance,
            adresse=adresse,
            cni_numero=cni_numero,
            cni_image=cni_image_path,
            cni_verifiee=False,
            mot_de_passe_hash=mot_de_passe_hash,
            salt=None,                # plus utilisé
            statut='en_attente',
            verifiee=False,
            date_creation=timezone.now()
        )

        return redirect('hacker_login')

class HackerHomeView(View):
    def get(self, request):
        hacker_id = request.session.get("hacker_id")

        if not hacker_id:
            return redirect("hacker_login")

        hacker = UserHacker.objects.get(id=hacker_id)

        context = {
            "hacker": hacker
        }

        return render(request, "hackerhome.html", context)
    

class HackerLogoutView(View):
     def get(self, request):
        request.session.flush()  # supprime toute la session
        return redirect('hacker_login')

def enterprise_register(request):
    if request.method == "POST":
        nom = request.POST.get("nom_legal")
        email = request.POST.get("email_entreprise")
        telephone = request.POST.get("telephone_entreprise")
        secteur = request.POST.get("secteur_activite")
        contact_nom = request.POST.get("contact_principal_nom")
        contact_email = request.POST.get("contact_principal_email")
        password = request.POST.get("mot_de_passe")
        registre_pdf = request.FILES.get("registre_commerce_pdf")  # PDF upload

        # Vérification doublon email
        if Enterprise.objects.filter(email_entreprise=email).exists():
            messages.error(request, "Email déjà utilisé.")
            return redirect("enterprise_register")

        # Création entreprise
        enterprise = Enterprise.objects.create(
            nom_legal=nom,
            email_entreprise=email,
            telephone_entreprise=telephone,
            secteur_activite=secteur,
            contact_principal_nom=contact_nom,
            contact_principal_email=contact_email,
            mot_de_passe_hash=make_password(password),
            registre_commerce_pdf=registre_pdf,  # Stockage du fichier + lien en BDD
        )

        messages.success(request, "Inscription réussie. En attente de validation.")
        return redirect("enterprise_login")

    return render(request, "enterprise_register.html")


# Login Entreprise
def enterprise_login(request):
    if request.method == "POST":
        email = request.POST.get("email_entreprise")
        password = request.POST.get("mot_de_passe")

        try:
            enterprise = Enterprise.objects.get(email_entreprise=email)
        except Enterprise.DoesNotExist:
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect("enterprise_login")

        if not check_password(password, enterprise.mot_de_passe_hash):
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect("enterprise_login")

        if not enterprise.verifiee:
            messages.error(request, "Compte non encore validé par l'administration.")
            return redirect("enterprise_login")

        # Session entreprise
        request.session["enterprise_id"] = enterprise.id
        return redirect("enterprise_dashboard")  # dashboard à créer

    return render(request, "enterprise_login.html")
