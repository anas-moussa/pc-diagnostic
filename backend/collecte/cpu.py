"""Collecte des informations sur le processeur (CPU)."""

import platform
import psutil  # bibliothèque installée dans le venv : lit CPU, RAM, disques...


def _lire_modele_cpu():
    """Renvoie le nom commercial du CPU, ou None si introuvable.
    (Le _ au début indique : fonction réservée à ce fichier.)"""
    systeme = platform.system()

    if systeme == "Windows":
        import winreg  # n'existe que sous Windows, donc importé ici seulement
        cle = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        )
        nom, _ = winreg.QueryValueEx(cle, "ProcessorNameString")
        return nom.strip()

    if systeme == "Linux":
        with open("/proc/cpuinfo", encoding="utf-8") as fichier:
            for ligne in fichier:
                if ligne.startswith("model name"):
                    return ligne.split(":", 1)[1].strip()

    return None


def collecter_cpu():
    """Renvoie un dictionnaire décrivant le processeur."""
    try:
        frequence = psutil.cpu_freq()  # peut valoir None sur certains PC
        return {
            "disponible": True,
            "modele": _lire_modele_cpu() or "inconnu",
            "coeurs_physiques": psutil.cpu_count(logical=False),
            "coeurs_logiques": psutil.cpu_count(logical=True),
            "frequence_max_mhz": round(frequence.max) if frequence else None,
            # interval=1 : psutil mesure pendant 1 seconde (sinon résultat peu fiable)
            "utilisation_pourcent": psutil.cpu_percent(interval=1),
        }
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
