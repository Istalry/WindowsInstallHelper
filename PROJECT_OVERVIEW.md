# Project Overview

## Objectif
Ce projet vise à créer un utilitaire Windows "portable" (Self-Contained) facilitant la transition d'un ancien PC vers un nouveau en matière d'installation de logiciels.

## Modes de Fonctionnement
L'outil opère en deux modes :
1. **Mode Export (PC Source)** : Analyse le registre Windows pour dresser la liste des logiciels installés, permet à l'utilisateur d'en faire le tri, et génère un fichier d'export JSON.
2. **Mode Import & Déploiement (PC Cible)** : Lit le fichier JSON, résout les installeurs via le gestionnaire de paquets `winget` ou via des exécutables locaux fournis par l'utilisateur, puis procède à l'installation automatisée en lot (batch) sur les disques choisis.

## Philosophie
*   **Pure installation**: L'outil ne migre pas les données utilisateurs (AppData, Registre utilisateur) pour garantir la stabilité et l'intégrité du nouveau système.
*   **100% Autonome**: Pas besoin d'installer Python. S'exécute en tant qu'un exécutable unique depuis une clé USB.



Blueprint Technique : Outil de Migration de Logiciels (PC)

1. Project Overview (Aperçu du Projet)

Ce projet vise à créer un utilitaire Windows "portable" (Self-Contained) facilitant la transition d'un ancien PC vers un nouveau. L'outil opère en deux modes :

Mode Export (PC Source) : Analyse le registre Windows pour dresser la liste des logiciels installés, permet à l'utilisateur d'en faire le tri, et génère un fichier d'export JSON.

Mode Import & Déploiement (PC Cible) : Lit le fichier JSON, résout les installeurs via le gestionnaire de paquets winget ou via des exécutables locaux fournis par l'utilisateur, puis procède à l'installation automatisée en lot (batch) sur les disques choisis.

Philosophie : Pure installation. L'outil ne migre pas les données utilisateurs (AppData, Registre utilisateur) pour garantir la stabilité et l'intégrité du nouveau système.

2. Stack de Développement

Langage : Python 3.11+

Interface Graphique (GUI) : CustomTkinter (basé sur Tkinter, offrant un design moderne, mode sombre natif et composants responsives).

Interactions Système : * winreg (Standard Python) pour la lecture sécurisée du registre.

subprocess pour l'exécution des commandes système et des installeurs.

Gestionnaire de Paquets : winget (Windows Package Manager, natif sous Windows 10/11).

Packaging & Déploiement : PyInstaller (Compilation avec les arguments --onefile et --noconsole pour générer un exécutable .exe unique et 100% autonome).

3. Fonctionnalités (Features)

Exécutable 100% Autonome (Self-Contained) : L'outil sera packagé sous la forme d'un unique fichier .exe. Il pourra être exécuté directement depuis une clé USB sur un PC vierge, sans nécessiter l'installation préalable de Python, de dépendances ou de bibliothèques graphiques.

Analyse du Registre (Registry Scanner) : Lecture de HKLM et HKCU (Uninstall keys) incluant les nœuds WOW6432Node pour lister les applications (Nom, Version, Éditeur).

Filtrage Intelligent : Exclusion automatique des composants systèmes critiques, des runtimes (C++, .NET) et des mises à jour Windows (KB).

Export / Import JSON : Sauvegarde et chargement de l'état de la sélection.

Barres de Progression Fonctionnelles (Feedback UI) : Intégration d'indicateurs visuels en temps réel. Une barre de progression sera affichée de manière fluide lors :

Du scan initial des registres.

De la génération du fichier d'export.

Du téléchargement et de l'installation en lot (batch) sur le nouveau PC.

Résolution Winget : Vérification automatique de la disponibilité d'un logiciel sur les dépôts officiels Microsoft.

Découverte Intelligente de Dossier (Auto-Scan) : Si un installeur manuel (.exe ou .msi) est sélectionné par l'utilisateur, l'outil scanne le dossier parent pour tenter de lier automatiquement les autres logiciels manquants du fichier d'import.

Moteur d'Installation Batch : Exécution séquentielle des installations (silencieuses via Winget avec argument --location, ou via l'interface standard pour les installeurs manuels).

4. Code Structure (Architecture)

Le projet suivra une architecture modulaire pour faciliter la maintenance :

migration_tool/
│
├── main.py                # Point d'entrée, initialisation de l'application
├── ui/                    # Module Interface Utilisateur
│   ├── __init__.py
│   ├── app_window.py      # Fenêtre principale (CustomTkinter)
│   ├── export_view.py     # Vue de la liste d'exportation (avec progress bar)
│   └── import_view.py     # Vue de configuration d'installation (avec progress bar)
│
├── core/                  # Logique métier
│   ├── __init__.py
│   ├── scanner.py         # Logique de lecture du registre winreg
│   ├── winget_api.py      # Wrapper pour les commandes subprocess winget
│   ├── file_manager.py    # Logique d'import/export JSON et découverte de dossiers
│   └── installer.py       # Moteur d'exécution des installations batch
│
├── utils/                 # Utilitaires transverses
│   ├── __init__.py
│   ├── logger.py          # Système de journalisation (logs)
│   └── config.py          # Constantes et chemins par défaut
│
└── requirements.txt       # Dépendances (CustomTkinter, etc.)


5. Naming Convention (Conventions de Nommage)

Le projet respectera strictement le standard Python PEP 8 :

Fichiers et Modules : snake_case.py (ex: app_window.py)

Classes : PascalCase (ex: RegistryScanner, MainWindow)

Fonctions et Méthodes : snake_case (ex: get_installed_software(), install_batch())

Variables : snake_case (ex: software_list, target_drive)

Constantes : UPPER_SNAKE_CASE (ex: REGISTRY_PATHS, EXCLUDED_KEYWORDS)

Variables privées : Préfixées par un underscore _ (ex: _current_state)

6. Code Guidelines (Règles de Développement)

Typage Strict (Type Hinting) : Toutes les fonctions doivent inclure des annotations de type pour les arguments et les retours (ex: def get_apps() -> list[dict]:).

Gestion des Erreurs (Error Handling) : Utilisation systématique des blocs try...except lors des interactions avec le registre, le système de fichiers ou les sous-processus. Les erreurs ne doivent jamais faire crasher silencieusement la GUI.

Journalisation (Logging) : Remplacement des print() par l'utilisation du module logging. Génération d'un fichier migration_tool.log dans le dossier temporaire pour faciliter le débogage.

Documentation (Docstrings) : Chaque classe et méthode publique doit posséder une docstring claire expliquant son rôle, ses arguments et ses retours.

UI Asynchrone (Crucial pour les Progress Bars) : Les opérations longues (scan du registre, installations, recherche winget) doivent impérativement être exécutées dans des threads séparés (via le module threading). Le fil d'exécution principal (Main Thread) sera réservé à la mise à jour de l'interface CustomTkinter (notamment pour faire avancer les barres de progression sans geler la fenêtre).