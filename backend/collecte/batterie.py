"""Collecte de l'état de la batterie (PC portable)."""

import psutil


def collecter_batterie():
    """Renvoie un dictionnaire décrivant la batterie, ou dit qu'il n'y en a pas."""
    try:
        batterie = psutil.sensors_battery()  # renvoie None s'il n'y a pas de batterie

        if batterie is None:
            return {
                "disponible": False,
                "raison": "aucune batterie détectée (PC fixe ?)",
            }

        # Temps restant : psutil renvoie des codes spéciaux quand il ne sait pas.
        secondes = batterie.secsleft
        if batterie.power_plugged or secondes in (
            psutil.POWER_TIME_UNKNOWN,
            psutil.POWER_TIME_UNLIMITED,
        ):
            autonomie_min = None  # branchée, ou durée inconnue : on n'invente rien
        else:
            autonomie_min = round(secondes / 60)

        return {
            "disponible": True,
            "niveau_pourcent": round(batterie.percent, 1),
            "branchee": batterie.power_plugged,        # True / False (None si inconnu)
            "autonomie_restante_min": autonomie_min,
            # L'usure demande une autre méthode (rapport Windows), prévue plus tard.
            "usure": {
                "disponible": False,
                "raison": "non mesurée pour l'instant (psutil ne la fournit pas)",
            },
        }
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
