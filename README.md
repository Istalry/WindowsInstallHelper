# Windows Install Helper (Migration Tool)

## 📌 Aperçu (Overview)
Cet utilitaire "portable" permet de faciliter la transition logicielle d'un ancien PC vers un nouveau PC sous Windows. Il opère en deux modes :
1. **Mode Export** : Scanne le registre de l'ancien PC et dresse l'état des lieux des logiciels installés, pour générer un JSON.
2. **Mode Import & Déploiement** : Lit le fichier JSON généré et automatise l'installation en lot directement sur la machine ou via l'interface `winget` et les installateurs locaux.

## ⚙️ Spécifications & Tech Stack
*   **Langage** : Python 3.11+
*   **Interface Graphique** : CustomTkinter
*   **Installation & Recherche** : standard `winreg` (registre local) & `subprocess` vers le binaire `winget`.
*   **Build** : S'exécute à partir des sources Python ou peut être packagé en exécutable (.exe) 100% autonome via PyInstaller.

## ✨ Fonctionnalités Avancées
*   **Vérification UAC** : Prévient l'utilisateur si l'application n'a pas les droits d'administrateur.
*   **Historique de Reprise** : Mémorise les logiciels déjà installés avec succès (fichier `.state`) pour éviter les doublons en cas de redémarrage de l'outil.
*   **Smart Folder Scan** : Cherche automatiquement à lier un fichier local d'installation à un nom de logiciel via du *Fuzzy Matching* (`difflib`).
*   **Détection d'Arguments Silencieux** : Analyse la signature binaire (`Inno Setup`, `NSIS`, `WiX`) des installeurs pour appliquer les bons flags silencieux automatiquement.

## ⚠️ Limitations Techniques
Ce projet a été imaginé et codé de façon expérimentale ("*Vibe Coded*") en cycle court. Par conséquent, **il ne sera plus officiellement maintenu**.

**Limitations inhérentes de l'application :**
- **Visibilité du registre** : L'outil scanne exclusivement les clés `Uninstall` du registre (HKLM, HKCU, et les noeuds WOW6432Node). Les programmes "portables" ou non-enregistrés via l'installeur officiel Windows n'apparaîtront jamais dans l'inventaire.
- **Paramètres Locaux Inconnus** : Les arguments d'installation silencieuse pour certains vieux `.exe` pourraient ne pas être pris en charge.

## 📄 Licence
Ce projet est open-source et distribué sous la Licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.
