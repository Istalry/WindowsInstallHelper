# Development Guidelines

## 1. Naming Convention (PEP 8)
*   **Fichiers et Modules :** `snake_case.py` (ex: `app_window.py`)
*   **Classes :** `PascalCase` (ex: `RegistryScanner`, `MainWindow`)
*   **Fonctions et Méthodes :** `snake_case` (ex: `get_installed_software()`, `install_batch()`)
*   **Variables :** `snake_case` (ex: `software_list`, `target_drive`)
*   **Constantes :** `UPPER_SNAKE_CASE` (ex: `REGISTRY_PATHS`, `EXCLUDED_KEYWORDS`)
*   **Variables privées :** Préfixées par un underscore `_` (ex: `_current_state`)

## 2. Code Guidelines (Règles strictes)
*   **Typage Strict (Type Hinting) :** Toutes les fonctions doivent inclure des annotations de type pour les arguments et les retours (ex: `def get_apps() -> list[dict]:`).
*   **Gestion des Erreurs (Error Handling) :** Utilisation systématique des blocs `try...except` lors des interactions avec le registre, le système de fichiers ou les sous-processus. Les erreurs ne doivent jamais faire crasher silencieusement la GUI.
*   **Journalisation (Logging) :** Remplacement des `print()` par l'utilisation du module `logging`. Génération d'un fichier `migration_tool.log` dans le dossier temporaire pour débugger au besoin.
*   **Documentation (Docstrings) :** Chaque classe et méthode publique doit posséder une docstring claire expliquant son rôle, ses arguments et ses retours.
*   **UI Asynchrone (Crucial) :** Les opérations longues (scan, installations) doivent impérativement être exécutées dans des threads séparés (via le module `threading`). Le fil d'exécution principal (Main Thread) sera réservé à la mise à jour de l'interface CustomTkinter (notamment les barres de progression).
*   **Historique et Reprise :** Les succès d'installation sont marqués dans un fichier adjascent `.state` au format JSON. Ne modifiez jamais le fichier source importé (`export.json` original).
*   **Modules Standards Préférés :** Pour limiter les dépendances et garantir la portabilité, privilégiez les modules standards Python (`ctypes`, `difflib`, `winreg`) plutôt que de télécharger des packages externes lourds.
