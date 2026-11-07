from django.db import migrations, models
import django.core.validators


def create_houses(apps, schema_editor):
    House = apps.get_model("points", "House")
    houses = [
        ("Gryffondor", "gryffondor", "gryffondor.png"),
        ("Serpentard", "serpentard", "serpentard.png"),
        ("Serdaigle", "serdaigle", "serdaigle.png"),
        ("Poufsouffle", "poufsouffle", "poufsouffle.png"),
    ]
    for nom, slug, image in houses:
        House.objects.get_or_create(
            slug=slug,
            defaults={"nom": nom, "image": image, "points": 0},
        )


def remove_houses(apps, schema_editor):
    House = apps.get_model("points", "House")
    House.objects.filter(
        slug__in=["gryffondor", "serpentard", "serdaigle", "poufsouffle"]
    ).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="House",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=50, unique=True, verbose_name="nom")),
                (
                    "slug",
                    models.SlugField(max_length=50, unique=True, verbose_name="identifiant"),
                ),
                (
                    "points",
                    models.IntegerField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="points",
                    ),
                ),
                ("image", models.CharField(max_length=100, verbose_name="fichier image")),
            ],
            options={
                "verbose_name": "maison",
                "verbose_name_plural": "maisons",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="PointLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("variation", models.IntegerField(verbose_name="variation")),
                ("motif", models.CharField(max_length=200, verbose_name="motif")),
                ("date", models.DateTimeField(auto_now_add=True, verbose_name="date")),
                (
                    "maison",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historique",
                        to="points.house",
                        verbose_name="maison",
                    ),
                ),
            ],
            options={
                "verbose_name": "mouvement de points",
                "verbose_name_plural": "historique des points",
                "ordering": ["-date"],
            },
        ),
        migrations.RunPython(create_houses, remove_houses),
    ]
