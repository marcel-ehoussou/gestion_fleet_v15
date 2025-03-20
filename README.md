# Système de Gestion de Flotte pour Odoo

## Vue d'ensemble
Ce projet se compose de deux modules complémentaires Odoo qui fournissent une solution complète de gestion de flotte :
1. `fleet_advanced_management` : Fonctionnalités de gestion de flotte de base
2. `fleet_dashboard` : Analyse avancée et suivi des KPI

## Modules

### Gestion Avancée de Flotte
Le module de base offre des capacités complètes de gestion de flotte, y compris :
- Gestion des véhicules
- Gestion des conducteurs
- Suivi des dépenses de carburant
- Planification de la maintenance
- Gestion des documents
- Système de réservation
- Analyse des coûts

### Tableau de Bord de Flotte
Le module de tableau de bord étend les fonctionnalités de base avec :
- Tableau de bord d'analyse en temps réel
- Système de suivi des KPI
- Graphiques et diagrammes interactifs
- Indicateurs de performance
- Suivi des expirations de documents
- Outils d'analyse financière

## Installation

### Prérequis
- Odoo 15 ou version ultérieure
- Python 3.8+
- PostgreSQL 12+

### Étapes d'installation
1. Clonez ce dépôt dans votre répertoire d'addons Odoo :
```bash
cd /path/to/odoo/addons
git clone https://github.com/your-repository/gestion_fleet.git
```

2. Mettez à jour votre fichier de configuration Odoo (`odoo.conf`) pour inclure le chemin vers ces modules :
```
addons_path = /path/to/odoo/addons,/path/to/odoo/addons/gestion_fleet
```

3. Redémarrez votre serveur Odoo :
```bash
service odoo restart
```

4. Installez les modules via l'interface Odoo :
   - Allez dans Apps
   - Supprimez le filtre 'Apps' et recherchez :
     - "Gestion Avancée de Flotte"
     - "Tableau de Bord de Flotte"
   - Installez les deux modules

## Configuration

### Configuration Initiale
1. **Groupes de Sécurité**
   - Utilisateur de Flotte : Accès de base aux opérations de flotte
   - Gestionnaire de Flotte : Accès complet à toutes les fonctionnalités
   - Utilisateur du Tableau de Bord de Flotte : Accès aux tableaux de bord
   - Gestionnaire du Tableau de Bord de Flotte : Droits de configuration des KPI

2. **Données de Base**
   - Configurer les types et catégories de véhicules
   - Configurer les profils des conducteurs
   - Définir les plannings de maintenance
   - Configurer les catégories de dépenses
   - Configurer les types de documents

3. **Configuration du Tableau de Bord**
   - Configurer les KPI et les objectifs
   - Personnaliser les mises en page du tableau de bord
   - Configurer les seuils d'alerte

## Fonctionnalités

### Gestion des Véhicules
- Gestion complète du cycle de vie des véhicules
- Planification et suivi de la maintenance
- Suivi de la consommation de carburant
- Suivi et analyse des coûts
- Gestion des documents

### Gestion des Conducteurs
- Profils et documentation des conducteurs
- Suivi et renouvellement des licences
- Suivi des performances
- Gestion des plannings

### Maintenance
- Planification de la maintenance préventive
- Suivi des réparations
- Historique des services
- Analyse des coûts
- Gestion des fournisseurs

### Réservations
- Système de réservation de véhicules
- Intégration du calendrier
- Prévention des conflits
- Suivi de l'utilisation
- Allocation des coûts

### Gestion des Documents
- Stockage et suivi des documents
- Notifications d'expiration
- Gestion des renouvellements
- Archive numérique des documents

### Analyse & Reporting
- Tableaux de bord complets
- Suivi des KPI
- Analyse des coûts
- Indicateurs de performance
- Génération de rapports personnalisés

## Utilisation

### Opérations de Base
1. **Gestion des Véhicules**
   ```
   Gestion de Flotte > Véhicules > Véhicules
   ```
   - Ajouter de nouveaux véhicules
   - Suivre l'état des véhicules
   - Surveiller les coûts

2. **Gestion des Conducteurs**
   ```
   Gestion de Flotte > Conducteurs > Conducteurs
   ```
   - Gérer les profils des conducteurs
   - Suivre les affectations
   - Surveiller les performances

3. **Maintenance**
   ```
   Gestion de Flotte > Opérations > Maintenance
   ```
   - Planifier les services
   - Suivre les réparations
   - Surveiller les coûts

4. **Réservations**
   ```
   Gestion de Flotte > Opérations > Réservations
   ```
   - Réserver des véhicules
   - Gérer les plannings
   - Suivre l'utilisation

### Opérations du Tableau de Bord
1. **Tableau de Bord Principal**
   ```
   Tableau de Bord de Flotte > Tableaux de Bord
   ```
   - Voir l'état général de la flotte
   - Surveiller les indicateurs clés
   - Suivre les performances

2. **Tableau de Bord des KPI**
   ```
   Tableau de Bord de Flotte > Tableau de Bord des KPI
   ```
   - Configurer les KPI
   - Définir les objectifs
   - Surveiller les tendances

## Développement

### Structure du Module
```
gestion_fleet/
├── README.md
├── fleet_advanced_management/
│   ├── README.md
│   ├── models/
│   │   ├── fleet_vehicle.py
│   │   ├── fleet_driver.py
│   │   ├── fleet_maintenance.py
│   │   ├── fleet_reservation.py
│   │   ├── fleet_expense.py
│   │   └── fleet_document.py
│   ├── views/
│   │   ├── fleet_vehicle_views.xml
│   │   ├── fleet_driver_views.xml
│   │   └── ...
│   └── security/
│       ├── ir.model.access.csv
│       └── fleet_security.xml
└── fleet_dashboard/
    ├── README.md
    ├── models/
    │   ├── fleet_dashboard.py
    │   └── fleet_kpi.py
    ├── static/
    │   └── src/
    │       ├── js/
    │       ├── css/
    │       └── xml/
    └── views/
        ├── dashboard_views.xml
        └── kpi_dashboard_views.xml
│       ├── css/
│       └── xml/
└── views/
    ├── dashboard_views.xml
    └── kpi_dashboard_views.xml
```

### Extension des Modules
- Suivre les mécanismes d'héritage d'Odoo
- Utiliser une gestion appropriée des dépendances
- Maintenir les configurations de sécurité
- Suivre les normes de codage

## Support
Pour le support et les rapports de bugs, veuillez créer un problème dans le dépôt ou contacter :
- Email : support@yourcompany.com
- Site Web : https://www.yourcompany.com

## Contribuer
1. Forker le dépôt
2. Créer une branche de fonctionnalité
3. Commiter vos modifications
4. Pousser vers la branche
5. Créer une Pull Request

## Licence
Ce projet est sous licence LGPL-3 - voir le fichier LICENSE pour plus de détails.

## Auteurs
- Nom de votre entreprise
- Liste des contributeurs

## Remerciements
- Communauté Odoo
- Contributeurs
- Utilisateurs fournissant des retours