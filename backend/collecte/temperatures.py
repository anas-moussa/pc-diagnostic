"""Collecte de la température du processeur.

Windows : on lit LibreHardwareMonitor (LHM) via son serveur web local.
Linux   : psutil lit directement les capteurs du système.
Si la donnée n'est pas accessible, on le dit clairement (rien n'est inventé).
"""

import json
import platform
import re
import urllib.error
import urllib.request

import psutil

# Adresse du serveur web de LHM (Options > Remote Web Server). 8085 = port par défaut.
URL_LHM = "http://localhost:8085/data.json"

# Noms de capteurs préférés, du plus fiable au moins fiable.
CAPTEURS_PREFERES = ["CPU Package", "Core Max", "Core (Tctl/Tdie)", "Core Average"]


def _vers_nombre(texte):
    """Transforme '64,0 °C' (ou '64.0 °C') en 64.0. Renvoie None si impossible."""
    trouve = re.search(r"-?\d+(?:[.,]\d+)?", str(texte))
    return float(trouve.group().replace(",", ".")) if trouve else None


def _parcourir(noeud):
    """Parcourt l'arbre de capteurs de LHM : le noeud, puis ses enfants, etc."""
    yield noeud
    for enfant in noeud.get("Children", []):
        yield from _parcourir(enfant)


def _temperatures_windows():
    """Lit les températures CPU depuis LibreHardwareMonitor."""
    try:
        with urllib.request.urlopen(URL_LHM, timeout=3) as reponse:
            arbre = json.loads(reponse.read().decode("utf-8"))
    except urllib.error.URLError:
        return {
            "disponible": False,
            "raison": "LibreHardwareMonitor n'est pas lancé (ou son serveur web est désactivé)",
        }

    capteurs = {}
    for noeud in _parcourir(arbre):
        identifiant = noeud.get("SensorId", "")
        est_cpu = identifiant.startswith(("/intelcpu/", "/amdcpu/"))
        est_temperature = "/temperature/" in identifiant
        # On écarte « Distance to TjMax » : c'est une marge, pas une température.
        if est_cpu and est_temperature and "Distance" not in noeud.get("Text", ""):
            valeur = _vers_nombre(noeud.get("Value"))
            if valeur is not None:
                capteurs[noeud["Text"]] = valeur

    return _resultat(capteurs, source="LibreHardwareMonitor")


def _temperatures_linux():
    """Lit les températures CPU via psutil (Linux uniquement)."""
    if not hasattr(psutil, "sensors_temperatures"):
        return {"disponible": False, "raison": "psutil ne fournit pas les températures ici"}

    capteurs = {}
    brut = psutil.sensors_temperatures()
    for nom_puce in ("coretemp", "k10temp", "zenpower", "cpu_thermal"):
        for entree in brut.get(nom_puce, []):
            etiquette = entree.label or nom_puce
            # On aligne les noms Linux sur ceux de LHM pour réutiliser _resultat.
            if etiquette == "Package id 0":
                etiquette = "CPU Package"
            elif etiquette == "Tctl":
                etiquette = "Core (Tctl/Tdie)"
            capteurs[etiquette] = entree.current

    return _resultat(capteurs, source="psutil")


def _resultat(capteurs, source):
    """Construit le dictionnaire final à partir des capteurs trouvés."""
    if not capteurs:
        return {"disponible": False, "raison": "aucun capteur de température CPU trouvé"}

    # On choisit le premier capteur préféré qui existe.
    nom_utilise = next((n for n in CAPTEURS_PREFERES if n in capteurs), None)
    if nom_utilise is None:
        nom_utilise = next(iter(capteurs))

    return {
        "disponible": True,
        "source": source,
        "cpu_c": capteurs[nom_utilise],
        "capteur_utilise": nom_utilise,
        "capteurs_c": capteurs,  # tous les capteurs trouvés (cœurs, moyenne...)
    }


def collecter_temperatures():
    """Renvoie la température du CPU, ou explique pourquoi elle est indisponible."""
    try:
        systeme = platform.system()
        if systeme == "Windows":
            return _temperatures_windows()
        if systeme == "Linux":
            return _temperatures_linux()
        return {"disponible": False, "raison": f"système non pris en charge : {systeme}"}
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
