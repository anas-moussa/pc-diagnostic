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
