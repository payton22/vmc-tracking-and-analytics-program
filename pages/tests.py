#from django.test import TestCase
from django.test import SimpleTestCase

# This is a test class that is simple for the moment as it 
# only checks the status code of all the webpages and esure
# that loading the pages do not cause any errors.
class SimpleTests(SimpleTestCase):
    def test_landing_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_page_status_code(self):
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 200)

    def test_import_page_status_code(self):
        response = self.client.get('/import/')
        self.assertEqual(response.status_code, 200)

    def test_visualizations_page_status_code(self):
        response = self.client.get('/visualizations/')
        self.assertEqual(response.status_code, 200)

    def test_vmcadmin_page_status_code(self):
        response = self.client.get('/vmcadmin/')
        self.assertEqual(response.status_code, 200)