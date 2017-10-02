from django.test import TestCase

from django.db import models

from pombola.core.models import Person, Position
from pombola.hansard.models import Sitting, Entry
from pombola.ghana.models import MP


class MPTestCase(TestCase):
    def setUp(self):
        self.person_mp = Person.objects.create(title="Dr.", legal_name="Kwesi Asante", slug="kwesi-asante")

        self.party_position = Position.objects.create(person=self.person_mp)
        self.parliament_position = Position.objects.create(person=self.person_mp)
        self.mp = MP.objects.create(person=self.person_mp,
                               party_position=self.party_position,
                               parliament_position=self.parliament_position,
                               first_name="Kwesi",
                          last_name="Asante")

    def test_mp_not_none(self):
        self.assertIsNotNone(self.mp)

    def test_mp_legal_name(self):
        self.assertEqual(self.mp.person.legal_name, 'Kwesi Asante')

    def test_mp_slug_not_null(self):
        self.assertNotEqual(self.mp.slug, '')

    def test_mp_slug_contains_first_and_last_names(self):
        self.assertIn(["kwesi", "asante"], self.mp.slug)

    # test slug if two MPs have the same first_name and last_name
