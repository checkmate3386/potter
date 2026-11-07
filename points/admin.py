from django.contrib import admin
from django.db import transaction

from .models import House, PointLog


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "points", "image")
    search_fields = ("nom", "slug")
    ordering = ("nom",)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous_points = None
        if change:
            previous_points = House.objects.values_list("points", flat=True).get(pk=obj.pk)
        super().save_model(request, obj, form, change)
        if previous_points is not None and previous_points != obj.points:
            PointLog.objects.create(
                maison=obj,
                variation=obj.points - previous_points,
                motif="Modification depuis l'administration",
            )


@admin.register(PointLog)
class PointLogAdmin(admin.ModelAdmin):
    list_display = ("date", "maison", "variation", "motif")
    list_filter = ("maison", "date")
    search_fields = ("maison__nom", "motif")
    readonly_fields = ("maison", "variation", "motif", "date")
    date_hierarchy = "date"
