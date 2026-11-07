from django.db import migrations


IMAGE_FILENAMES = {
    "gryffondor": "gryffindor.webp",
    "serpentard": "slytherin.jpeg",
    "serdaigle": "ravenclaw.webp",
    "poufsouffle": "hufflepuff.webp",
}


def update_house_images(apps, schema_editor):
    House = apps.get_model("points", "House")
    for slug, filename in IMAGE_FILENAMES.items():
        House.objects.filter(slug=slug).update(image=filename)


def restore_default_images(apps, schema_editor):
    House = apps.get_model("points", "House")
    for slug in IMAGE_FILENAMES:
        House.objects.filter(slug=slug).update(image=f"{slug}.png")


class Migration(migrations.Migration):
    dependencies = [
        ("points", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(update_house_images, restore_default_images),
    ]
