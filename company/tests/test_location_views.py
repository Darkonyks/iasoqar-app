from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput

from company.company_models import Company, OstalaLokacija
from company.location_forms import LocationForm


class LocationCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.company = Company.objects.create(
            name='Test Company',
            pib='123456789',
            mb='12345678'
        )
        
    def test_location_form_without_company_id_shows_dropdown(self):
        """Test da forma bez company_id parametra prikazuje dropdown za kompaniju"""
        form = LocationForm()
        # Proveri da company polje nije skriveno
        self.assertNotIsInstance(form.fields['company'].widget, HiddenInput)
        
    def test_location_form_with_company_id_hides_dropdown(self):
        """Test da forma sa company_id parametrom sakriva dropdown za kompaniju"""
        form = LocationForm(company_id=self.company.id)
        # Proveri da je company polje skriveno
        self.assertIsInstance(form.fields['company'].widget, HiddenInput)
        # Proveri da je kompanija postavljena kao inicijalna vrednost
        self.assertEqual(form.fields['company'].initial, self.company)
        
    def test_location_create_view_with_company_parameter(self):
        """Test da LocationCreateView koristi company_id iz URL parametra"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('company:location_create')
        response = self.client.get(url, {'company': self.company.id})
        
        self.assertEqual(response.status_code, 200)
        # Proveri da je kompanija prosleđena u kontekst
        self.assertEqual(response.context['company'], self.company)
        # Proveri da je title ispravno postavljen
        expected_title = f'Nova lokacija za kompaniju {self.company.name}'
        self.assertEqual(response.context['title'], expected_title)
        
    def test_location_create_view_without_company_parameter(self):
        """Test da LocationCreateView radi i bez company parametra"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('company:location_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Proveri da kompanija nije u kontekstu
        self.assertNotIn('company', response.context)
        # Proveri da je title generički
        self.assertEqual(response.context['title'], 'Nova lokacija')
        
    def test_location_create_post_with_company_parameter(self):
        """Test kreiranje lokacije sa company parametrom"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('company:location_create')
        data = {
            'name': 'Test Lokacija',
            'street': 'Test Ulica',
            'street_number': '123',
            'city': 'Beograd',
            'postal_code': '11000',
            'country': 'Srbija',
            'notes': 'Test napomena'
        }
        
        response = self.client.post(url + f'?company={self.company.id}', data)
        
        # Proveri da je lokacija kreirana
        self.assertTrue(OstalaLokacija.objects.filter(name='Test Lokacija').exists())
        
        # Proveri da je lokacija povezana sa ispravnom kompanijom
        location = OstalaLokacija.objects.get(name='Test Lokacija')
        self.assertEqual(location.company, self.company)
        
        # Proveri da je redirect na company detail
        self.assertRedirects(response, reverse('company:detail', kwargs={'pk': self.company.pk}))
