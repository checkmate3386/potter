from django.db import transaction
from django.db.models import F

from .models import House, PointLog


class InsufficientPointsError(Exception):
    pass


@transaction.atomic
def apply_points(house_id, variation, motif):
    house = House.objects.get(pk=house_id)
    minimum_points = max(0, -variation)
    updated = House.objects.filter(
        pk=house_id,
        points__gte=minimum_points,
    ).update(points=F("points") + variation)
    if not updated:
        raise InsufficientPointsError
    house.refresh_from_db(fields=["points"])
    PointLog.objects.create(maison=house, variation=variation, motif=motif)
    return house
