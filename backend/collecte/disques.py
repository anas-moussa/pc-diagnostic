"""Collecte des informations sur les disques (partitions et espace)."""

import psutil

OCTETS_PAR_GO = 1024 ** 3


def _en_go(octets):
    """Convertit des octets en Go, arrondi à 2 décimales."""
    return round(octets / OCTETS_PAR_GO, 2)


def collecter_partitions():
    """Renvoie la liste des partitions avec leur capacité et leur espace libre.

    Une partition = une « tranche » de disque, par exemple C: sous Windows.
    """
    try:
        partitions = []
        # all=False : on ignore les systèmes de fichiers virtuels (Linux surtout)
        for partition in psutil.disk_partitions(all=False):
            # Sous Windows, un lecteur CD vide fait échouer disk_usage :
            # on traite chaque partition dans son propre try.
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except (PermissionError, OSError) as erreur:
                partitions.append({
                    "disponible": False,
                    "point_montage": partition.mountpoint,
                    "raison": str(erreur),
                })
                continue

            partitions.append({
                "disponible": True,
                "point_montage": partition.mountpoint,   # ex. "C:\\" ou "/"
                "systeme_fichiers": partition.fstype,    # ex. "NTFS", "ext4"
                "total_go": _en_go(usage.total),
                "utilise_go": _en_go(usage.used),
                "libre_go": _en_go(usage.free),
                "utilisation_pourcent": usage.percent,
            })

        return {"disponible": True, "partitions": partitions}
    except Exception as erreur:
        return {"disponible": False, "raison": str(erreur)}
