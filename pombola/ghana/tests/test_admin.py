from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.urls import resolve

from pombola.core.admin import PersonAdmin
from pombola.images.admin import ImageAdminInline
from ghana.models import MP, GhanaMP


class GhanaMPAdminTest(TestCase):
    def setUp(self):
        self.username = 'odekro_admin'
        self.password = 'W@90U_1'
        self.email = 'site.admin@odekro.org'
        self.user = User.objects.create_user(self.username,
                                             self.email,
                                             self.password)
        self.user.is_staff = True
        self.user.is_superuser = True

        MP.objects.all().delete()
        GhanaMP.objects.all().delete()

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_if_user_can_login_into_admin(self):
        login_response = self.client.login(username=self.username,
                                           password=self.password)
        self.assertTrue(login_response)

    def test_MP_model_has_no_instance(self):
        self.assertEqual(MP.objects.count(), 0)

    def test_GhanaMP_model_has_no_instance(self):
        self.assertEqual(GhanaMP.objects.count(), 0)

    def test_add_MP(self):
        post_data = {
            'title': 'Mr.',
            'legal name': 'Kwesi Asante',
            'gender': 'male',
            'date of birth': '1969-12-31',
            'date of death': '',
            'email': 'kwesi.asante@gmail.com',
            'first name': 'Kwesi',
            'last name': 'Asante',
            'middle name': '',
        }
        response = self.client.post(
            resolve('/admin/ghana/ghanamp/add/'),
            post_data
        )
        self.assertEquals(MP.objects.count(), 1)
        self.assertEquals(GhanaMP.objects.count(), 1)
