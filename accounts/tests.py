from django.test import TestCase
from django.urls import reverse, resolve
from .views import signup

class SignupTests(TestCase):
    def test_signup_view_response(self):
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # def test_signup_url_resolvers(self):
    #     view = resolve('/signup/')
    #     self.assrtEqual(view.func, signup)