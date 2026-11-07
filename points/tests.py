import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.finders import find
from django.test import TestCase, override_settings
from django.urls import reverse

from .actions import ActionsConfigError, load_actions
from .models import House, PointLog


class PointsViewsTests(TestCase):
    def setUp(self):
        self.house = House.objects.get(slug="gryffondor")

    def test_public_pages_are_available_without_a_shared_code(self):
        response = self.client.get(reverse("accueil"))
        self.assertContains(response, "/static/img/gryffindor.webp")
        self.assertEqual(
            self.client.get(reverse("maison", args=[self.house.slug])).status_code,
            200,
        )
        self.assertEqual(self.client.get(reverse("ajouter")).status_code, 200)
        self.assertEqual(self.client.get(reverse("depenser")).status_code, 200)
        self.assertEqual(
            response["X-Robots-Tag"], "noindex, nofollow, noarchive, nosnippet"
        )

    def test_house_logos_use_existing_jpeg_and_webp_files(self):
        expected_images = {
            "gryffondor": "gryffindor.webp",
            "serpentard": "slytherin.jpeg",
            "serdaigle": "ravenclaw.webp",
            "poufsouffle": "hufflepuff.webp",
        }
        for slug, filename in expected_images.items():
            with self.subTest(house=slug):
                house = House.objects.get(slug=slug)
                self.assertEqual(house.image, filename)
                self.assertIsNotNone(find(f"img/{filename}"))

    def test_action_adds_points_and_creates_history(self):
        with patch(
            "points.views.load_actions",
            return_value=[{"nom": "Bonne réponse", "points": 5}],
        ):
            response = self.client.post(
                reverse("maison", args=[self.house.slug]), {"action_index": "0"}
            )
        self.house.refresh_from_db()
        self.assertRedirects(response, reverse("maison", args=[self.house.slug]))
        self.assertEqual(self.house.points, 5)
        self.assertEqual(PointLog.objects.get().variation, 5)

    def test_negative_action_cannot_make_total_negative(self):
        with patch(
            "points.views.load_actions",
            return_value=[{"nom": "Oubli", "points": -5}],
        ):
            self.client.post(
                reverse("maison", args=[self.house.slug]), {"action_index": "0"}
            )
        self.house.refresh_from_db()
        self.assertEqual(self.house.points, 0)
        self.assertFalse(PointLog.objects.exists())

    def test_spending_cannot_make_total_negative(self):
        response = self.client.post(
            reverse("depenser"),
            {"maison": self.house.pk, "points": "1"},
        )
        self.house.refresh_from_db()
        self.assertEqual(self.house.points, 0)
        self.assertFalse(PointLog.objects.exists())
        self.assertContains(response, "ne possède pas assez de points")

    def test_manual_addition_succeeds(self):
        response = self.client.post(
            reverse("ajouter"),
            {"maison": self.house.pk, "points": "12"},
        )
        self.house.refresh_from_db()
        self.assertRedirects(response, reverse("accueil"))
        self.assertEqual(self.house.points, 12)
        self.assertEqual(PointLog.objects.get().motif, "Ajout manuel")

    def test_robots_txt_and_header(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(response.content.decode(), "User-agent: *\nDisallow: /\n")
        self.assertEqual(
            response["X-Robots-Tag"], "noindex, nofollow, noarchive, nosnippet"
        )

    def test_invalid_house_selection_shows_error_instead_of_server_error(self):
        response = self.client.post(
            reverse("ajouter"),
            {"maison": "not-a-house", "points": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sélectionnez une maison valide.")


class HouseAdminTests(TestCase):
    def test_manual_admin_point_change_is_recorded(self):
        house = House.objects.get(slug="gryffondor")
        admin_user = get_user_model().objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        self.client.force_login(admin_user)
        response = self.client.post(
            reverse("admin:points_house_change", args=[house.pk]),
            {
                "nom": house.nom,
                "slug": house.slug,
                "points": "25",
                "image": house.image,
                "_save": "Enregistrer",
            },
        )
        self.assertEqual(response.status_code, 302)
        log = PointLog.objects.get(maison=house)
        self.assertEqual(log.variation, 25)
        self.assertEqual(log.motif, "Modification depuis l'administration")


class ActionsConfigTests(TestCase):
    @override_settings(BASE_DIR=Path("/not-a-real-project"))
    def test_missing_actions_file_reports_clear_error(self):
        with self.assertRaisesRegex(ActionsConfigError, "introuvable"):
            load_actions()

    def test_invalid_json_reports_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory) / "config"
            config_dir.mkdir()
            (config_dir / "actions.json").write_text("{invalid", encoding="utf-8")
            with override_settings(BASE_DIR=Path(directory)):
                with self.assertRaisesRegex(ActionsConfigError, "JSON invalide"):
                    load_actions()

    def test_loads_valid_actions_including_negative_values(self):
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory) / "config"
            config_dir.mkdir()
            (config_dir / "actions.json").write_text(
                json.dumps({"actions": [{"nom": "Pénalité", "points": -5}]}),
                encoding="utf-8",
            )
            with override_settings(BASE_DIR=Path(directory)):
                self.assertEqual(
                    load_actions(), [{"nom": "Pénalité", "points": -5}]
                )
