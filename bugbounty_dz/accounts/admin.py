from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import UserHacker, Enterprise

@admin.register(UserHacker)
class UserHackerAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'prenom',
        'nom',
        'telephone',
        'verifiee',
        'statut',
        'date_creation',
        'cni_preview',
    )

    search_fields = ('email', 'nom', 'prenom', 'telephone')
    list_filter = ('verifiee', 'statut', 'date_creation')

    readonly_fields = ('cni_preview',)

    def cni_preview(self, obj):
        if obj.cni_image:
            image_url = '/media/' + obj.cni_image

            return format_html(
                '''
                <a href="{}" target="_blank">
                    <img src="{}" style="
                        max-height: 80px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        cursor: zoom-in;
                    " />
                </a>
                ''',
                image_url,
                image_url
            )
        return "Aucune image"

    cni_preview.short_description = "Photo CIN"


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = (
        'nom_legal',
        'email_entreprise',
        'telephone_entreprise',
        'secteur_activite',
        'contact_principal_nom',
        'contact_principal_email',
        'statut',
        'verifiee',
        'date_creation',
        'registre_commerce_preview',
    )

    search_fields = ('nom_legal', 'email_entreprise', 'telephone_entreprise')
    list_filter = ('statut', 'verifiee', 'date_creation')

    # Champs en lecture seule
    readonly_fields = (
        'registre_commerce_preview',
        'date_creation',
        'date_activation',
        'date_modification',
    )

    # Organisation de la page détail
    fieldsets = (
        ('Informations générales', {
            'fields': (
                'nom_legal',
                'email_entreprise',
                'telephone_entreprise',
                'secteur_activite',
                'description_entreprise',
                'logo_entreprise',
                'site_web',
            )
        }),
        ('Contact principal', {
            'fields': (
                'contact_principal_nom',
                'contact_principal_poste',
                'contact_principal_email',
                'contact_principal_telephone',
            )
        }),
        ('Registre de commerce', {
            'fields': (
                'registre_commerce_pdf',
                'registre_commerce_preview',
            )
        }),
        ('Statut et validation', {
            'fields': (
                'statut',
                'verifiee',
                'date_creation',
                'date_activation',
                'date_modification',
            )
        }),
    )

    # Aperçu du PDF
    def registre_commerce_preview(self, obj):
        if obj.registre_commerce_pdf:
            return format_html(
                '<a href="{}" target="_blank">📄 Voir le registre (PDF)</a>',
                obj.registre_commerce_pdf.url
            )
        return "Aucun PDF"

    registre_commerce_preview.short_description = "Registre de commerce"

    # Action admin pour valider
    actions = ['valider_compte']

    def valider_compte(self, request, queryset):
        updated = queryset.update(verifiee=True, statut='actif')
        self.message_user(request, f"{updated} entreprise(s) validée(s).")

    valider_compte.short_description = "Valider les comptes sélectionnés"
