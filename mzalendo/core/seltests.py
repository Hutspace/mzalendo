from django.core.urlresolvers import reverse
from django_selenium.testcases import SeleniumTestCase
from django.core.management import call_command 

class MyTestCase(SeleniumTestCase):
    

    def test_home(self):
        self.open_url(reverse('home'))
        self.failUnless(self.is_text_present('Mzalendo'))
        self.assertEquals(self.get_title(), 'Home :: Mzalendo')


    def test_static(self):
        """Test that the static files are being served"""

        # run the collectstatic command - so that all the static files can be served.
        call_command('collectstatic', interactive=False) 

        self.open_url('/static/static_test.txt')
        self.assertTrue( 'static serving works!' in self.page_source )


    def test_404(self):
        """Test that the static files are being served"""
        self.open_url('/hash/bang/bosh')
        self.assertTrue( 'Page Not Found - 404' in self.text)
