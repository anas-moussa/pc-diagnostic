"""Collecte des informations générales sur le système (OS, nom de la machine)."""

import platform  # module standard de Python : infos sur l'OS (aucune installation)
import socket    # module standard : sert ici à lire le nom de la machine


def collecter_systeme():
    """Renvoie un dictionnaire décrivant le système d'exploitation."""
    try:
        return {
            "disponible": True,
            "os": platform.system(),          # "Windows" ou "Linux"
            "version": platform.version(),    # numéro de build détaillé
            "release": platform.release(),    # ex. "10" ou "11" sous Windows
            "architecture": platform.machine(),  # ex. "AMD64"
            "nom_machine": socket.gethostname(),
        }
    except Exception as erreur:
        # Si quelque chose casse, on le dit clairement au lieu de planter.
        return {"disponible": False, "raison": str(erreur)}
