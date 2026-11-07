import json

from django.conf import settings


class ActionsConfigError(Exception):
    pass


def load_actions():
    path = settings.BASE_DIR / "config" / "actions.json"
    try:
        with path.open(encoding="utf-8") as actions_file:
            data = json.load(actions_file)
    except FileNotFoundError as exc:
        raise ActionsConfigError(
            "Le fichier config/actions.json est introuvable."
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ActionsConfigError(
            "Le fichier config/actions.json est illisible ou contient un JSON invalide."
        ) from exc

    actions = data.get("actions") if isinstance(data, dict) else None
    if not isinstance(actions, list):
        raise ActionsConfigError(
            'Le fichier config/actions.json doit contenir une liste "actions".'
        )

    validated_actions = []
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            raise ActionsConfigError(f"L'action n°{index} doit être un objet JSON.")
        name = action.get("nom")
        points = action.get("points")
        if not isinstance(name, str) or not name.strip():
            raise ActionsConfigError(f"Le nom de l'action n°{index} est manquant.")
        if isinstance(points, bool) or not isinstance(points, int):
            raise ActionsConfigError(
                f"Le nombre de points de l'action n°{index} doit être un entier."
            )
        validated_actions.append({"nom": name.strip(), "points": points})
    return validated_actions
