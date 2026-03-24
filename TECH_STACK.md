# Tech Stack

## Langage & Base
*   **Python:** 3.11+

## Interface Graphique (GUI)
*   **CustomTkinter:** Basé sur Tkinter, offrant un design moderne, un mode sombre natif et des composants responsibles.

## Interactions Système
*   **`winreg` (Standard Python):** Pour la recherche et la lecture sécurisée du registre (Désinstallations HKLM, HKCU, WOW6432Node).
*   **`subprocess`:** Pour l'exécution non-bloquante des commandes système, `winget` et installeurs locaux.
*   **`threading`:** Pour gérer l'asynchronisme de l'interface et éviter les blocages lors d'opérations longues.

## Gestionnaire de Paquets
*   **`winget`:** Windows Package Manager, natif sous Windows 10/11 pour le téléchargement et l'installation silencieuse.

## Packaging & Déploiement
*   **PyInstaller:** Compilation de l'application en utilisant les arguments `--onefile` et `--noconsole` pour générer un exécutable `.exe` unique et autonome.
