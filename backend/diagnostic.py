"""Point d'entrée : lance toutes les collectes et produit un fichier JSON.

Utilisation (depuis n'importe quel dossier) :
    python backend/diagnostic.py
"""

import json
from datetime import datetime
from pathlib import Path  # Path : manipule des chemins de fichiers proprement

from collecte.batterie import collecter_batterie
from collecte.cpu import collecter_cpu
from collecte.disques import collecter_partitions
from collecte.memoire import collecter_memoire
from collecte.sante_disques import collecter_sante_disques
from collecte.systeme import collecter_systeme
from collecte.temperatures import collecter_temperatures

# __file__ = ce fichier. On remonte d'un dossier (backend) puis on va dans data/.
# Ainsi le chemin est correct, que tu lances le programme depuis backend ou la racine.
DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"
FICHIER_SORTIE = DOSSIER_DATA / "dernier_diagnostic.json"


def _executer(collecte):
    """Lance une collecte. Si elle plante malgré tout, on le dit au lieu de tout arrêter."""
    try:
        return collecte()
    except Exception as erreur:
        return {"disponible": False, "raison": f"erreur inattendue : {erreur}"}


def lancer_diagnostic():
    """Exécute toutes les collectes et renvoie le diagnostic complet (un dictionnaire)."""
    return {
        # isoformat : date lisible par les machines, ex. 2026-10-15T00:50:12+01:00
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        "version_schema": 1,  # numéro de version du format JSON (utile plus tard)
        "systeme": _executer(collecter_systeme),
        "cpu": _executer(collecter_cpu),
        "memoire": _executer(collecter_memoire),
        "disques": {
            "partitions": _executer(collecter_partitions),
            "sante": _executer(collecter_sante_disques),
        },
        "batterie": _executer(collecter_batterie),
        "temperatures": _executer(collecter_temperatures),
    }


def enregistrer(diagnostic):
    """Écrit le diagnostic dans data/dernier_diagnostic.json."""
    DOSSIER_DATA.mkdir(exist_ok=True)  # crée data/ s'il n'existe pas
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as fichier:
        json.dump(diagnostic, fichier, indent=2, ensure_ascii=False)


# Ce bloc ne s'exécute que si on lance CE fichier directement
# (et pas quand un autre fichier l'importe, ce qui servira avec FastAPI).
if __name__ == "__main__":
    resultat = lancer_diagnostic()
    enregistrer(resultat)
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
    print(f"\nDiagnostic enregistré dans : {FICHIER_SORTIE}")
