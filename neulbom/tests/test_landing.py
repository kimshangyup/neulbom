"""
Tests for neulbom project views.
"""

from django.test import TestCase, Client
from django.urls import reverse


class LandingPageTest(TestCase):
    """Test cases for public landing page"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_landing_page_loads(self):
        """Test that landing page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_landing_page_accessible_without_authentication(self):
        """Test that landing page is accessible without login"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_page_displays_program_name(self):
        """Test that page displays program name"""
        response = self.client.get('/')
        self.assertContains(response, '늘봄학교')

    def test_landing_page_displays_program_description(self):
        """Test that page displays program description"""
        response = self.client.get('/')
        self.assertContains(response, '서울시 초등학생을 위한 방과후 교육 프로그램')

    def test_landing_page_displays_program_mission(self):
        """Test that page displays program mission"""
        response = self.client.get('/')
        self.assertContains(response, '13개 대학과 함께하는 초등학생 맞춤형 교육')

    def test_landing_page_has_login_button(self):
        """Test that page has login button linking to login page"""
        response = self.client.get('/')
        self.assertContains(response, '/accounts/login/')
        self.assertContains(response, '로그인')

    def test_landing_page_has_participating_schools_section(self):
        """Test that page displays participating schools section"""
        response = self.client.get('/')
        self.assertContains(response, '참여 대학')

    def test_landing_page_context_data(self):
        """Test that view passes correct context data"""
        response = self.client.get('/')
        self.assertEqual(response.context['program_name'], '늘봄학교')
        self.assertEqual(response.context['program_description'], '서울시 초등학생을 위한 방과후 교육 프로그램')
        self.assertEqual(response.context['program_mission'], '13개 대학과 함께하는 초등학생 맞춤형 교육')

    def test_landing_page_has_semantic_html(self):
        """Test that page uses semantic HTML5 elements"""
        response = self.client.get('/')
        content = response.content.decode()

        # Check for semantic elements
        self.assertIn('<header', content)
        self.assertIn('<nav', content)
        self.assertIn('<main>', content)
        self.assertIn('<section', content)
        self.assertIn('<footer', content)

    def test_landing_page_has_proper_heading_hierarchy(self):
        """Test that page has proper heading hierarchy"""
        response = self.client.get('/')
        content = response.content.decode()

        # Should have h1, h2, h3 tags
        self.assertIn('<h1', content)
        self.assertIn('<h2', content)
        self.assertIn('<h3', content)

    def test_landing_page_has_aria_labels(self):
        """Test that page has ARIA labels for accessibility"""
        response = self.client.get('/')
        content = response.content.decode()

        # Check for ARIA attributes
        self.assertIn('aria-label', content)
        self.assertIn('aria-labelledby', content)

    def test_landing_page_has_korean_lang_attribute(self):
        """Test that page has Korean language attribute"""
        response = self.client.get('/')
        self.assertContains(response, '<html lang="ko">')

    def test_landing_page_has_meta_viewport(self):
        """Test that page has viewport meta tag for responsive design"""
        response = self.client.get('/')
        self.assertContains(response, 'name="viewport"')

    def test_landing_page_has_meta_description(self):
        """Test that page has meta description for SEO"""
        response = self.client.get('/')
        self.assertContains(response, 'name="description"')

    def test_landing_page_url_name(self):
        """Test that landing page URL name resolves correctly"""
        url = reverse('landing')
        self.assertEqual(url, '/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
