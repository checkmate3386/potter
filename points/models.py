from django.core.validators import MinValueValidator
from django.db import models


class House(models.Model):
    nom = models.CharField("nom", max_length=50, unique=True)
    slug = models.SlugField("identifiant", max_length=50, unique=True)
    points = models.IntegerField("points", default=0, validators=[MinValueValidator(0)])
    image = models.CharField("fichier image", max_length=100)

    class Meta:
        ordering = ["id"]
        verbose_name = "maison"
        verbose_name_plural = "maisons"

    def __str__(self):
        return self.nom


class PointLog(models.Model):
    maison = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="historique",
        verbose_name="maison",
    )
    variation = models.IntegerField("variation")
    motif = models.CharField("motif", max_length=200)
    date = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "mouvement de points"
        verbose_name_plural = "historique des points"

    def __str__(self):
        return f"{self.maison} : {self.variation:+d} ({self.motif})"
