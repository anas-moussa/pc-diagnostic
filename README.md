# pc-diagnostic

Application de diagnostic de PC (Windows et Linux) : lecture du matériel, santé des disques, températures, batterie, tests de stress, puis analyse avec estimation de l'état, des pièces à risque et du prix en dinars tunisiens (TND).

> Projet en cours de construction.

## Fonctionnalités prévues

- Diagnostic local, puis mode réseau (agent) et mode clé USB bootable
- Moteur de règles : note de santé sur 100 et pièces à risque
- Analyse en langage humain avec une IA locale (Ollama), optionnelle
- Estimation du prix d'occasion en TND, avec conversion vers d'autres devises
- Rapport PDF, historique des diagnostics, mode « j'achète un PC d'occasion »
- Interface web au thème PC, mode sombre, plusieurs langues

## Structure

```
pc-diagnostic/
├── backend/     # Python : collecte, règles, IA, rapport
├── frontend/    # Interface web
├── data/        # prix.json, historique
└── README.md
```

## Technologies

- [psutil](https://github.com/giampaolo/psutil) : infos CPU, RAM, disques
- [smartmontools](https://www.smartmontools.org) : santé des disques (SMART)
- [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) : températures sous Windows
- [FastAPI](https://fastapi.tiangolo.com) : backend
- [Vite](https://vite.dev) et [React](https://react.dev) : interface
- [Ollama](https://ollama.com) : IA locale gratuite (optionnelle)
- [ReportLab](https://www.reportlab.com) : rapports PDF

## Installation (backend)

```
pip install -r backend/requirements.txt
```
## Phase 1 : diagnostic local (état actuel)

Le programme lit le matériel du PC et produit un fichier JSON.

### Ce qui est collecté
| Section | Contenu |
|---|---|
| `systeme` | OS, version, architecture, nom de la machine |
| `cpu` | modèle, cœurs, fréquence nominale, utilisation |
| `memoire` | RAM totale, utilisée, libre |
| `disques` | partitions (espace libre) et santé S.M.A.R.T. via `smartctl` |
| `batterie` | niveau, branchée ou non, autonomie estimée |
| `temperatures` | température du CPU (LibreHardwareMonitor sous Windows) |

**Principe :** si une donnée n'est pas accessible, la section contient
`"disponible": false` et la raison. Rien n'est inventé.

### Prérequis
- Python 3.12
- *(optionnel)* [smartmontools](https://www.smartmontools.org/) pour la santé des disques
- *(optionnel, Windows)* [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
  lancé en administrateur, avec **Options → Remote Web Server → Run**,
  pour la température du processeur

### Installation (Windows, PowerShell)
```powershell
git clone https://github.com/anas-moussa/pc-diagnostic.git
cd pc-diagnostic\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Sous Linux : `source .venv/bin/activate` à la place de la ligne d'activation.

### Lancement
Depuis la racine du projet, avec l'environnement virtuel activé :
```powershell
python backend\diagnostic.py
```
Le JSON s'affiche et est enregistré dans `data/dernier_diagnostic.json`
(fichier ignoré par Git : il contient le nom de la machine).

### État des tests
- Windows 11 : testé
- Linux : code prévu, pas encore testé
- Disques SATA : lecture prévue, pas encore testée (seul un SSD NVMe a été testé)
- Usure de la batterie : non mesurée pour l'instant
