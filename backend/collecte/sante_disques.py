"""Collecte de la santé des disques via smartctl (données S.M.A.R.T.)."""

import json
import shutil      # shutil.which : cherche si un programme existe sur le PC
import subprocess  # permet à Python de lancer un autre programme (ici smartctl)


def _lancer_smartctl(arguments):
    """Lance smartctl avec --json et renvoie le résultat sous forme de dictionnaire."""
    resultat = subprocess.run(
        ["smartctl", *arguments, "--json"],
        capture_output=True,  # on récupère ce que smartctl affiche
        text=True,
        timeout=30,           # on n'attend pas plus de 30 secondes
    )
    # smartctl renvoie un code de sortie non nul pour plein de raisons, même
    # sans vraie panne : on ne s'y fie pas, on lit simplement le JSON.
    return json.loads(resultat.stdout)


def _premier_message(donnees):
    """Extrait le premier message d'erreur de smartctl, s'il y en a un."""
    messages = donnees.get("smartctl", {}).get("messages", [])
    return messages[0].get("string") if messages else None


def _lire_disque(nom, type_disque):
    """Lit la santé d'un disque. Renvoie un dictionnaire."""
    donnees = _lancer_smartctl(["-a", "-d", type_disque, nom])

    # Pas de réponse utile : on dit pourquoi (souvent : droits administrateur).
    if "device" not in donnees or "smart_status" not in donnees:
        raison = _premier_message(donnees) or "aucune donnée SMART renvoyée"
        return {"disponible": False, "peripherique": nom, "raison": raison}

    disque = {
        "disponible": True,
        "peripherique": nom,
        "type": donnees["device"].get("type"),                 # "nvme", "sat"...
        "modele": donnees.get("model_name"),
        "firmware": donnees.get("firmware_version"),
        "capacite_go": round(donnees.get("user_capacity", {}).get("bytes", 0) / 1e9, 1),
        "sante_globale_ok": donnees["smart_status"].get("passed"),  # True / False
        "temperature_c": donnees.get("temperature", {}).get("current"),
        # Volontairement SANS numéro de série (repo public, vie privée).
    }

    # --- SSD NVMe ---
    nvme = donnees.get("nvme_smart_health_information_log")
    if nvme:
        disque.update({
            "usure_pourcent": nvme.get("percentage_used"),
            "spare_disponible_pourcent": nvme.get("available_spare"),
            "spare_seuil_pourcent": nvme.get("available_spare_threshold"),
            "alerte_critique": nvme.get("critical_warning"),
            # 1 « data unit » = 512 000 octets ; on convertit en téraoctets
            "ecrit_to": round(nvme.get("data_units_written", 0) * 512_000 / 1e12, 2),
            "lu_to": round(nvme.get("data_units_read", 0) * 512_000 / 1e12, 2),
            "heures_allumage": nvme.get("power_on_hours"),
            "extinctions_brutales": nvme.get("unsafe_shutdowns"),
            "erreurs_integrite": nvme.get("media_errors"),
        })

    # --- Disque SATA (HDD ou SSD) : quelques attributs clés ---
    table = donnees.get("ata_smart_attributes", {}).get("table")
    if table:
        attributs = {ligne["id"]: ligne["raw"]["value"] for ligne in table}
        disque.update({
            "heures_allumage": donnees.get("power_on_time", {}).get("hours"),
            "secteurs_realloues": attributs.get(5),        # ID 5 : secteurs défectueux remplacés
            "secteurs_en_attente": attributs.get(197),     # ID 197 : secteurs suspects
            "secteurs_incorrigibles": attributs.get(198),  # ID 198 : secteurs illisibles
        })

    return disque


def collecter_sante_disques():
    """Renvoie la santé de tous les disques détectés par smartctl."""
    if shutil.which("smartctl") is None:
        return {"disponible": False, "raison": "smartctl n'est pas installé ou introuvable dans le PATH"}

    try:
        scan = _lancer_smartctl(["--scan"])
        peripheriques = scan.get("devices", [])
        if not peripheriques:
            return {
                "disponible": False,
                "raison": _premier_message(scan)
                or "aucun disque détecté (essaie avec les droits administrateur)",
            }

        disques = [_lire_disque(p["name"], p["type"]) for p in peripheriques]
        return {"disponible": True, "disques": disques}
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
