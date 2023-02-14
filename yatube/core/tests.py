from http import HTTPStatus

from django.test import TestCase
from faker import Faker

fake = Faker()


class ViewTestClass(TestCase):
    def test_error_page_404(self):
        response = self.client.get(fake.pystr(min_chars=3, max_chars=13))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
