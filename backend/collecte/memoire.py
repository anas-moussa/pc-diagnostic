"""Collecte des informations sur la mémoire RAM."""

import psutil

OCTETS_PAR_GO = 1024 ** 3  # 1 Go = 1024 x 1024 x 1024 octets


def _en_go(octets):
    """Convertit des octets en Go, arrondi à 2 décimales."""
    return round(octets / OCTETS_PAR_GO, 2)


def collecter_memoire():
    """Renvoie un dictionnaire décrivant la RAM."""
    try:
        ram = psutil.virtual_memory()
        return {
            "disponible": True,
            "total_go": _en_go(ram.total),
            "utilisee_go": _en_go(ram.used),
            "libre_go": _en_go(ram.available),
            "utilisation_pourcent": ram.percent,
        }
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
