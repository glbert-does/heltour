from django.test import TestCase
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import User


class AdminSearchTestCase(TestCase):
    def test_all_search_fields(self):
        superuser = User(
            username='superuser',
            password='Password',
            is_superuser=True,
            is_staff=True,
        )
        superuser.save()
        self.client.force_login(user=superuser)
        for model_class, admin_class in admin.site._registry.items():
            with self.subTest(model_class._meta.model_name):
                path = reverse(f'admin:{model_class._meta.app_label}_{model_class._meta.model_name}_changelist')
                response = self.client.get(path + "?q=whatever")
                self.assertEqual(response.status_code, 200)
