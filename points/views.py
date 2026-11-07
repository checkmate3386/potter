from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .access import SESSION_ACCESS_KEY, access_code_matches, shared_code_required
from .actions import ActionsConfigError, load_actions
from .models import House
from .services import InsufficientPointsError, apply_points


@require_http_methods(["GET", "POST"])
def access(request):
    if request.session.get(SESSION_ACCESS_KEY):
        return redirect("accueil")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    if request.method == "POST":
        if access_code_matches(request.POST.get("code", "")):
            request.session.cycle_key()
            request.session[SESSION_ACCESS_KEY] = True
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            messages.success(request, "Accès autorisé.")
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("accueil")
        messages.error(request, "Code d'accès incorrect.")

    if not settings.ACCESS_CODE:
        messages.error(
            request,
            "Le code d'accès n'est pas configuré. Définissez la variable ACCESS_CODE.",
        )
    return render(request, "points/access.html", {"next": next_url})


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /\n",
        content_type="text/plain; charset=utf-8",
    )


@shared_code_required
def home(request):
    houses = House.objects.all()
    return render(request, "points/home.html", {"maisons": houses})


@shared_code_required
@require_http_methods(["GET", "POST"])
def house_detail(request, slug):
    house = get_object_or_404(House, slug=slug)
    if request.method == "POST":
        try:
            actions = load_actions()
        except ActionsConfigError as exc:
            messages.error(request, str(exc))
            return redirect("maison", slug=house.slug)

        try:
            action_index = int(request.POST.get("action_index", ""))
            if action_index < 0:
                raise IndexError
            action = actions[action_index]
        except (ValueError, IndexError):
            messages.error(request, "Cette action n'est pas valide.")
            return redirect("maison", slug=house.slug)

        try:
            updated_house = apply_points(
                house.pk, action["points"], action["nom"]
            )
        except InsufficientPointsError:
            messages.error(
                request,
                "Cette action ferait passer le total de la maison sous zéro point.",
            )
        else:
            messages.success(
                request,
                f"{action['points']:+d} points pour {updated_house.nom}.",
            )
        return redirect("maison", slug=house.slug)

    try:
        actions = load_actions()
        actions_error = ""
    except ActionsConfigError as exc:
        actions = []
        actions_error = str(exc)
    return render(
        request,
        "points/house.html",
        {"maison": house, "actions": actions, "actions_error": actions_error},
    )


@shared_code_required
@require_http_methods(["GET", "POST"])
def spend_points(request):
    return _manual_points_form(request, operation="spend")


@shared_code_required
@require_http_methods(["GET", "POST"])
def add_points(request):
    return _manual_points_form(request, operation="add")


def _manual_points_form(request, operation):
    houses = House.objects.all()
    selected_house = None
    amount = ""
    if request.method == "POST":
        amount = request.POST.get("points", "").strip()
        selected_house_id = request.POST.get("maison", "")
        try:
            amount_value = int(amount)
            if amount_value <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Saisissez un nombre entier de points supérieur à zéro.")
        else:
            try:
                selected_house = House.objects.get(pk=selected_house_id)
            except (House.DoesNotExist, TypeError, ValueError):
                messages.error(
                    request,
                    "Sélectionnez une maison valide.",
                )
            else:
                variation = amount_value if operation == "add" else -amount_value
                motif = "Ajout manuel" if operation == "add" else "Dépense manuelle"
                try:
                    updated_house = apply_points(selected_house.pk, variation, motif)
                except InsufficientPointsError:
                    messages.error(
                        request,
                        f"{selected_house.nom} ne possède pas assez de points. "
                        "Son total ne peut pas descendre sous zéro.",
                    )
                else:
                    messages.success(
                        request,
                        f"{amount_value} point(s) "
                        f"{'ajouté(s) à' if operation == 'add' else 'dépensé(s) par'} "
                        f"{updated_house.nom}. Nouveau total : {updated_house.points}.",
                    )
                    return redirect("accueil")

    return render(
        request,
        "points/manual_points.html",
        {
            "maisons": houses,
            "operation": operation,
            "selected_house": selected_house,
            "amount": amount,
        },
    )
