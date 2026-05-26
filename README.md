# 🏠 VOMASI - Gestion des cotisations

Application mobile de gestion des cotisations pour l'association **VOMASI**.  
Permet de suivre les paiements, gérer les bénéficiaires et exporter des rapports.

---

## 📱 Fonctionnalités

| Fonction | Description |
|----------|-------------|
| 🔐 **Accès sécurisé** | Protection par identifiant / mot de passe |
| 👥 **Gestion des membres** | Ajouter, modifier, supprimer des membres |
| 💰 **Paiement séparé** | Cotisation (10 000 FCFA) et restauration (1 000 FCFA) |
| 🟢🔴 **Suivi visuel** | Icônes vertes/rouges pour voir qui a payé |
| 📅 **Date limite** | Fixer une date butoir pour les cotisations |
| 👑 **Bénéficiaire** | Désigner qui reçoit les fonds |
| 📊 **Statistiques** | Visualiser le taux de collecte |
| 📄 **Fiche récapitulative** | Générer un rapport complet |
| 📁 **Export CSV** | Exporter les données en fichier Excel |
| ⚠️ **Alertes retards** | Identifier les membres non à jour |

---

## 💰 Règles de cotisation

| Type | Montant |
|------|---------|
| Cotisation principale | **10 000 FCFA** |
| Restauration | **1 000 FCFA** |
| Total par membre | **11 000 FCFA** |

- 📅 Périodicité : **tous les 2 mois** (60 jours)
- 👑 Le bénéficiaire est choisi par la présidente selon les besoins des membres

---

## 🔐 Accès à l'application

| Champ | Valeur |
|-------|--------|
| Identifiant | `presidente` |
| Mot de passe | `vomasi2025` |

---

## 📸 Aperçu

```

┌─────────────────────────────────┐
│  🟢    KONE Adama               │
│  🔴    📍 Abobo                  │
│        ⚠️ Restauration due       │
│        [💰 10000] [🍽️ 1000] [🗑️] │
└─────────────────────────────────┘

```

| Icône | Signification |
|-------|---------------|
| 🟢 | Cotisation payée |
| 🔴 | Cotisation ou restauration impayée |
| 🟠 | Cycle de 2 mois dépassé |

---

## 📱 Installation

### Sur Android (recommandé)

1. Ouvre le lien : `https://tonpseudo.github.io/vomasi/`
2. Appuie sur les **3 points** (Chrome) → **"Ajouter à l'écran d'accueil"**
3. Nomme : **"VOMASI"**
4. L'application s'utilise comme une app native

### Depuis un fichier local

```bash
# Ouvrir avec Chrome
file:///chemin/vers/vomasi_app.html
```

---

📁 Structure du projet

```
vomasi/
├── index.html          # Application principale
└── README.md           # Documentation
```

---

🛠️ Technologies utilisées

Technologie Usage
HTML5 Structure
CSS3 Styles et interface
JavaScript Logique métier
LocalStorage Base de données locale
PWA Installation sur mobile

---

📄 Export CSV

Le fichier exporté contient :

· Nom et prénom de chaque membre
· Localité et téléphone
· Date de paiement de la cotisation
· Statut (payé / non payé)
· Récapitulatif des totaux

---

👥 Rôles

Rôle Responsabilités
Présidente - Gère les membres - Enregistre les paiements - Désigne le bénéficiaire - Remet les fonds
Membres Paient la cotisation (10 000 + 1 000 FCFA)

---

📊 Flux de travail

```
1. Ajouter les membres
         ↓
2. Fixer une date limite
         ↓
3. Enregistrer les paiements
         ↓
4. Suivre le total collecté
         ↓
5. Désigner le bénéficiaire
         ↓
6. Remettre la somme
         ↓
7. Générer la fiche récapitulative
         ↓
8. Cycle suivant (réinitialisation)
```

---

🔒 Sécurité

· Authentification requise pour accéder à l'application
· Données stockées localement (pas de serveur externe)
· Aucune donnée transmise sur Internet

---

🐛 Résolution des problèmes courants

Problème Solution
L'application ne s'ouvre pas Vérifier que le fichier est en .html
Les données disparaissent Ne pas effacer le cache du navigateur
Mot de passe oublié Contacter l'administrateur
Export ne fonctionne pas Vérifier les permissions de stockage

---

📞 Support

Pour toute question ou suggestion :

· Association VOMASI
· Email : kalouflash@gmail.com
· Téléphone : [numéro de contact]

---

📅 Version

Version actuelle : 1.0.0
Dernière mise à jour : Mai 2026

---

🙏 Remerciements

Développé pour l'association VOMASI afin de faciliter la gestion des cotisations et le soutien aux membres dans le besoin.

---

📜 Licence

Application privée - Usage exclusif de l'association VOMASI
