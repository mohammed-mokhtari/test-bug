from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

# Configuration Administration
class AdminConfig(models.Model):
    """Configuration globale du système"""
    cle = models.CharField(max_length=100, unique=True)
    valeur = models.CharField(max_length=500, null=True, blank=True)
    type_valeur = models.CharField(
        max_length=50,
        choices=[
            ('integer', 'Integer'),
            ('decimal', 'Decimal'),
            ('json', 'JSON'),
            ('string', 'String'),
        ],
        null=True,
        blank=True
    )
    description = models.TextField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_config'
        verbose_name = 'Configuration Admin'
        verbose_name_plural = 'Configurations Admin'

    def __str__(self):
        return self.cle


# Utilisateurs Admin
class AdminUser(models.Model):
    """Utilisateurs administrateurs du système"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('moderateur', 'Modérateur'),
        ('support', 'Support'),
    ]

    email = models.EmailField(unique=True)
    nom_complet = models.CharField(max_length=255, null=True, blank=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)
    permissions = models.JSONField(default=dict, null=True, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_connexion = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Utilisateur Admin'
        verbose_name_plural = 'Utilisateurs Admin'

    def __str__(self):
        return self.email


# Utilisateurs Hackers
class UserHacker(models.Model):
    """Profils des hackers/chercheurs en sécurité"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('desactive', 'Désactivé'),
    ]

    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.TextField()
    photo_profil = models.CharField(max_length=255, null=True, blank=True)
    cni_image = models.CharField(max_length=255, null=True, blank=True)
    cni_numero = models.CharField(max_length=50, unique=True, null=True, blank=True)
    cni_verifiee = models.BooleanField(default=False)
    nationalite = models.CharField(max_length=50, default='Algérie')
    mot_de_passe_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, null=True, blank=True)
    solde_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    revenus_totaux = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente')
    verifiee = models.BooleanField(default=False)
    bio = models.TextField(null=True, blank=True)
    linkedin_url = models.CharField(max_length=255, null=True, blank=True)
    github_url = models.CharField(max_length=255, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_activation = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_hackers'
        verbose_name = 'Hacker'
        verbose_name_plural = 'Hackers'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['telephone']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"


# Entreprises
class Enterprise(models.Model):
    """Profils des entreprises participant au programme"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('desactive', 'Désactivé'),
    ]

    nom_legal = models.CharField(max_length=255)
    email_entreprise = models.EmailField(unique=True)
    telephone_entreprise = models.CharField(max_length=20, null=True, blank=True)
    secteur_activite = models.CharField(max_length=100, null=True, blank=True)
    registre_commerce_pdf = models.FileField(
        upload_to='registre_commerce/',  # le dossier dans MEDIA
        db_column='registre_commerce',
        null=True,
        blank=True
    )
    registre_image = models.CharField(max_length=255, null=True, blank=True)
    contact_principal_nom = models.CharField(max_length=100, null=True, blank=True)
    contact_principal_poste = models.CharField(max_length=100, null=True, blank=True)
    contact_principal_email = models.EmailField(null=True, blank=True)
    contact_principal_telephone = models.CharField(max_length=20, null=True, blank=True)
    logo_entreprise = models.CharField(max_length=255, null=True, blank=True)
    site_web = models.CharField(max_length=255, null=True, blank=True)
    description_entreprise = models.TextField(null=True, blank=True)
    mot_de_passe_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255, null=True, blank=True)
    solde_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    solde_depense = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente')
    verifiee = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_activation = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enterprises'
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'

    def __str__(self):
        return self.nom_legal


# Membres de l'Entreprise
class EnterpriseMember(models.Model):
    """Membres autorisés au sein d'une entreprise"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Manager'),
        ('reviewer', 'Relecteur'),
        ('member', 'Membre'),
    ]

    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='membres')
    email = models.EmailField()
    nom_complet = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enterprise_members'
        verbose_name = 'Membre Entreprise'
        verbose_name_plural = 'Membres Entreprise'
        unique_together = ('enterprise', 'email')

    def __str__(self):
        return f"{self.nom_complet} - {self.enterprise.nom_legal}"


# Programmes de Bug Bounty
class Program(models.Model):
    """Programmes de bug bounty créés par les entreprises"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Privé'),
    ]
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('termine', 'Terminé'),
    ]

    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='programmes')
    nom = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    portee = models.TextField(null=True, blank=True)
    regles_programme = models.TextField(null=True, blank=True)
    budget_total = models.DecimalField(max_digits=15, decimal_places=2)
    budget_restant = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    budget_depense = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    montant_minimum_bug = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    types_vulnerabilites_acceptees = models.CharField(max_length=500, null=True, blank=True)
    domaines_acceptes = models.CharField(max_length=500, null=True, blank=True)
    severites_acceptees = models.CharField(max_length=500, null=True, blank=True)
    recompenses_config = models.JSONField(default=dict, null=True, blank=True)
    visibilite = models.CharField(max_length=50, choices=VISIBILITY_CHOICES, default='public')
    hackers_invites = models.TextField(null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programs'
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
        indexes = [
            models.Index(fields=['enterprise']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return self.nom


# Participants du Programme
class ProgramParticipant(models.Model):
    """Hackers participants à un programme"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='participants')
    hacker = models.ForeignKey(UserHacker, on_delete=models.CASCADE, related_name='programmes_participation')
    date_participation = models.DateTimeField(auto_now_add=True)
    nombre_rapports_soumis = models.IntegerField(default=0)
    nombre_rapports_acceptes = models.IntegerField(default=0)

    class Meta:
        db_table = 'program_participants'
        verbose_name = 'Participant Programme'
        verbose_name_plural = 'Participants Programme'
        unique_together = ('program', 'hacker')

    def __str__(self):
        return f"{self.hacker.prenom} {self.hacker.nom} - {self.program.nom}"


# Rapports de Bug
class Report(models.Model):
    """Rapports de bugs soumis par les hackers"""
    STATUT_CHOICES = [
        ('soumis', 'Soumis'),
        ('en_revision', 'En révision'),
        ('accepte', 'Accepté'),
        ('rejete', 'Rejeté'),
        ('en_correction', 'En correction'),
        ('corrige', 'Corrigé'),
        ('paye', 'Payé'),
        ('publie', 'Publié'),
    ]
    SEVERITE_CHOICES = [
        ('Critique', 'Critique'),
        ('Élevée', 'Élevée'),
        ('Moyenne', 'Moyenne'),
        ('Basse', 'Basse'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='rapports')
    hacker = models.ForeignKey(UserHacker, on_delete=models.CASCADE, related_name='rapports')
    numero_reference = models.CharField(max_length=50, unique=True, null=True, blank=True)
    titre = models.CharField(max_length=255)
    description = models.TextField()
    type_vulnerabilite = models.CharField(max_length=100, null=True, blank=True)
    severite_cvss = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    severite_label = models.CharField(max_length=50, choices=SEVERITE_CHOICES, null=True, blank=True)
    etapes_reproduction = models.TextField(null=True, blank=True)
    impact_description = models.TextField(null=True, blank=True)
    fichiers_attaches = models.JSONField(default=list, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='soumis')
    montant_propose = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_final = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_acceptance = models.DateTimeField(null=True, blank=True)
    date_correction = models.DateTimeField(null=True, blank=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    raison_refus = models.TextField(null=True, blank=True)
    notes_moderateur = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
        indexes = [
            models.Index(fields=['program']),
            models.Index(fields=['hacker']),
            models.Index(fields=['statut']),
            models.Index(fields=['severite_label']),
            models.Index(fields=['date_soumission']),
        ]

    def __str__(self):
        return f"{self.titre} ({self.numero_reference})"


# Sessions
class Session(models.Model):
    """Sessions utilisateur"""
    USER_TYPE_CHOICES = [
        ('hacker', 'Hacker'),
        ('enterprise', 'Entreprise'),
        ('admin', 'Admin'),
    ]

    user_id = models.IntegerField(null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, null=True, blank=True)
    token_jwt = models.CharField(max_length=500)
    token_refresh = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    date_derniere_activite = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sessions'
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['user_type']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        return f"Session {self.user_type} - {self.date_creation}"


# Transactions
class Transaction(models.Model):
    """Transactions financières (paiements aux hackers)"""
    TYPE_TRANSACTION_CHOICES = [
        ('paiement_bug', 'Paiement Bug'),
        ('bonus', 'Bonus'),
        ('refund', 'Remboursement'),
        ('retrait', 'Retrait'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('completee', 'Complétée'),
        ('rejetee', 'Rejetée'),
        ('annulee', 'Annulée'),
    ]

    hacker = models.ForeignKey(UserHacker, on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=50, choices=TYPE_TRANSACTION_CHOICES, null=True, blank=True)
    montant_brut = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    commission_plateforme = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    montant_net = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente')
    numero_compte_baridimob = models.CharField(max_length=50, null=True, blank=True)
    numero_compte_masque = models.CharField(max_length=20, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    raison_refus = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_completion = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['hacker']),
            models.Index(fields=['statut']),
            models.Index(fields=['type_transaction']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        return f"Transaction {self.id} - {self.hacker.email}"


# Disputes
class Dispute(models.Model):
    """Litiges entre hackers et entreprises"""
    TYPE_DISPUTE_CHOICES = [
        ('montant', 'Montant en désaccord'),
        ('rejet_injuste', 'Rejet injuste'),
        ('délai', 'Délai de paiement'),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_revision', 'En révision'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    ]

    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True, related_name='disputes')
    hacker = models.ForeignKey(UserHacker, on_delete=models.SET_NULL, null=True, blank=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True, blank=True)
    type_dispute = models.CharField(max_length=100, choices=TYPE_DISPUTE_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='ouvert')
    resolution = models.TextField(null=True, blank=True)
    compensation_proposee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'disputes'
        verbose_name = 'Dispute'
        verbose_name_plural = 'Disputes'

    def __str__(self):
        return f"Dispute {self.id} - {self.type_dispute}"


# Messages Chat
class MessageChat(models.Model):
    """Messages de discussion sur un rapport"""
    TYPE_AUTEUR_CHOICES = [
        ('hacker', 'Hacker'),
        ('enterprise', 'Entreprise'),
        ('admin', 'Admin'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='messages')
    hacker = models.ForeignKey(UserHacker, on_delete=models.SET_NULL, null=True, blank=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.SET_NULL, null=True, blank=True)
    admin = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
    contenu = models.TextField()
    type_auteur = models.CharField(max_length=50, choices=TYPE_AUTEUR_CHOICES, null=True, blank=True)
    fichiers_attaches = models.JSONField(default=list, null=True, blank=True)
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages_chat'
        verbose_name = 'Message Chat'
        verbose_name_plural = 'Messages Chat'

    def __str__(self):
        return f"Message {self.id} - Report {self.report.id}"


# Notifications
class Notification(models.Model):
    """Notifications utilisateurs"""
    TYPE_NOTIFICATION_CHOICES = [
        ('bug_accepte', 'Bug accepté'),
        ('bug_rejete', 'Bug rejeté'),
        ('paiement', 'Paiement'),
        ('nouveau_message', 'Nouveau message'),
        ('programme_invite', 'Invitation programme'),
        ('autre', 'Autre'),
    ]

    hacker = models.ForeignKey(UserHacker, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    type_notification = models.CharField(max_length=100, choices=TYPE_NOTIFICATION_CHOICES, null=True, blank=True)
    titre = models.CharField(max_length=255, null=True, blank=True)
    contenu = models.TextField(null=True, blank=True)
    lien_cible = models.CharField(max_length=255, null=True, blank=True)
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.type_notification} - {self.titre}"


# Leaderboard
class Leaderboard(models.Model):
    """Classement des hackers"""
    BADGE_CHOICES = [
        ('novice', 'Novice'),
        ('confirmé', 'Confirmé'),
        ('expert', 'Expert'),
        ('maître', 'Maître'),
    ]

    hacker = models.OneToOneField(UserHacker, on_delete=models.CASCADE, related_name='leaderboard')
    bugs_acceptes = models.IntegerField(default=0)
    bugs_critiques = models.IntegerField(default=0)
    bugs_eleves = models.IntegerField(default=0)
    bugs_moyens = models.IntegerField(default=0)
    bugs_bas = models.IntegerField(default=0)
    revenu_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    taux_acceptation = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    position = models.IntegerField(null=True, blank=True)
    points_total = models.IntegerField(default=0)
    badge = models.CharField(max_length=100, choices=BADGE_CHOICES, null=True, blank=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leaderboard'
        verbose_name = 'Leaderboard'
        verbose_name_plural = 'Leaderboards'

    def __str__(self):
        return f"{self.hacker.prenom} {self.hacker.nom} - Position {self.position}"


# Logs d'Activité
class LogActivite(models.Model):
    """Logs de toutes les actions du système"""
    USER_TYPE_CHOICES = [
        ('hacker', 'Hacker'),
        ('enterprise', 'Entreprise'),
        ('admin', 'Admin'),
    ]
    ENTITE_TYPE_CHOICES = [
        ('report', 'Rapport'),
        ('program', 'Programme'),
        ('user', 'Utilisateur'),
        ('transaction', 'Transaction'),
        ('dispute', 'Dispute'),
    ]

    user_id = models.IntegerField(null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, null=True, blank=True)
    action = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    entite_type = models.CharField(max_length=50, choices=ENTITE_TYPE_CHOICES, null=True, blank=True)
    entite_id = models.IntegerField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'logs_activite'
        verbose_name = 'Log Activité'
        verbose_name_plural = 'Logs Activité'

    def __str__(self):
        return f"{self.user_type} - {self.action} - {self.date_action}"


# Tokens de Vérification
class VerificationToken(models.Model):
    """Tokens pour vérification d'email et réinitialisation de mot de passe"""
    TYPE_TOKEN_CHOICES = [
        ('email_verification', 'Vérification Email'),
        ('password_reset', 'Réinitialisation Mot de Passe'),
        ('account_activation', 'Activation Compte'),
    ]
    USER_TYPE_CHOICES = [
        ('hacker', 'Hacker'),
        ('enterprise', 'Entreprise'),
        ('admin', 'Admin'),
    ]

    user_id = models.IntegerField(null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, null=True, blank=True)
    token = models.CharField(max_length=500, unique=True)
    type_token = models.CharField(max_length=50, choices=TYPE_TOKEN_CHOICES, null=True, blank=True)
    utilisé = models.BooleanField(default=False, db_column='utilisé')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    date_utilisation = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'verification_tokens'
        verbose_name = 'Token Vérification'
        verbose_name_plural = 'Tokens Vérification'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['utilisé']),
        ]

    def __str__(self):
        return f"{self.type_token} - {self.user_id}"
    


class Submission(models.Model):
    hacker = models.ForeignKey(UserHacker, on_delete=models.CASCADE)
    program = models.ForeignKey('Program', on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    statut = models.CharField(max_length=50, default="en_cours")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre
