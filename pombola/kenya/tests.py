import json
import re
import urllib
import urlparse

from django.core.urlresolvers import reverse

from pombola.experiments.models import Event, Experiment
from pombola.feedback.models import Feedback
from .views import EXPERIMENT_DATA

from django_webtest import WebTest

from nose.plugins.attrib import attr

@attr(country='kenya')
class CountyPerformancePageTests(WebTest):

    def setUp(self):
        experiment_slug = 'mit-county-larger'
        self.data = EXPERIMENT_DATA[experiment_slug]
        self.url = '/' + self.data['base_view_name']
        self.sid = self.data['qualtrics_sid']
        self.experiment = Experiment.objects.create(
            slug=experiment_slug,
            name='MIT County Performance experiment')

    def tearDown(self):
        self.experiment.delete()
        Feedback.objects.all().delete()

    def test_page_view(self):
        response = self.app.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.html.get('a', {'id': 'share-facebook'}))
        self.assertTrue(response.html.get('a', {'id': 'share-twitter'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'surveyPromoBanner'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'opportunity'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'threat'}))

    def test_threat_variant(self):
        response = self.app.get(self.url + '?variant=t')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'threat'})))
        self.assertFalse(
            response.html.findAll('div', {'id': 'opportunity'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'social-context'}))

    def test_opportunity_variant(self):
        response = self.app.get(self.url + '?variant=o')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'opportunity'})))
        self.assertFalse(
            response.html.findAll('div', {'id': 'threat'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'social-context'}))

    def test_neither_variant(self):
        response = self.app.get(self.url + '?variant=n')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            response.html.findAll('div', {'id': 'opportunity'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'threat'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'social-context'}))

    def test_threat_variant_with_social_context(self):
        response = self.app.get(self.url + '?variant=ts')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'threat'})))
        self.assertFalse(
            response.html.findAll('div', {'id': 'opportunity'}))
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'social-context'})))

    def test_opportunity_variant_with_social_context(self):
        response = self.app.get(self.url + '?variant=os')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'opportunity'})))
        self.assertFalse(
            response.html.findAll('div', {'id': 'threat'}))
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'social-context'})))

    def test_neither_variant_with_social_context(self):
        response = self.app.get(self.url + '?variant=ns')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            response.html.findAll('div', {'id': 'opportunity'}))
        self.assertFalse(
            response.html.findAll('div', {'id': 'threat'}))
        self.assertEqual(
            1, len(response.html.findAll('div', {'id': 'social-context'})))

    def test_petition_submission(self):
        Event.objects.all().delete()
        response = self.app.get(self.url + '?variant=o&g=f&agroup=over&utm_expid=1234')
        event = Event.objects.get(
            variant='o',
            category='page',
            action='view',
            label=self.data['pageview_label'])
        user_key = re.search(r'^\d+$', event.user_key).group()
        extra_data = json.loads(event.extra_data)
        self.assertEqual('f', extra_data['g'])
        self.assertEqual('over', extra_data['agroup'])
        form = response.forms.get('petition')
        form['name'] = 'Joe Bloggs'
        form['email'] = 'hello@example.org'
        form.submit()
        self.assertEqual(
            Feedback.objects.filter(
               status='non-actionable',
                email='hello@example.org',
                comment__contains='Joe Bloggs').count(),
            1)
        event = Event.objects.get(
            variant='o',
            category='form',
            action='submit',
            label='petition')
        self.assertEqual(user_key, event.user_key)
        extra_data = json.loads(event.extra_data)
        self.assertEqual('f', extra_data['g'])

    def test_senate_submission(self):
        Event.objects.all().delete()
        test_comment = "Some comment to submit"
        response = self.app.get(self.url + '?variant=t&g=m&agroup=over&utm_expid=1234')
        event = Event.objects.get(
            variant='t',
            category='page',
            action='view',
            label=self.data['pageview_label'])
        user_key = re.search(r'^\d+$', event.user_key).group()
        extra_data = json.loads(event.extra_data)
        self.assertEqual('m', extra_data['g'])
        self.assertEqual('over', extra_data['agroup'])
        form = response.forms.get('senate')
        form['comments'] = test_comment
        form.submit()
        self.assertEqual(
            Feedback.objects.filter(
               status='non-actionable',
                comment__contains=test_comment).count(),
            1)
        event = Event.objects.get(
            variant='t',
            category='form',
            action='submit',
            label='senate')
        self.assertEqual(user_key, event.user_key)
        extra_data = json.loads(event.extra_data)
        self.assertEqual('m', extra_data['g'])

    def test_survey_link(self):
        Event.objects.all().delete()
        response = self.app.get(self.url + '?variant=n&g=f&agroup=under&utm_expid=1234')
        event = Event.objects.get(
            variant='n',
            category='page',
            action='view',
            label=self.data['pageview_label'])
        user_key = re.search(r'^\d+$', event.user_key).group()
        extra_data = json.loads(event.extra_data)
        self.assertEqual('f', extra_data['g'])
        self.assertEqual('under', extra_data['agroup'])
        survey_url = response.html.find('a', {'id': 'take-survey'})['href']
        parsed_url = urlparse.urlparse(survey_url)
        self.assertEqual(parsed_url.path,
                         reverse(self.data['base_view_name'] + '-survey'))
        # Follow that link, but don't follow the redirect:
        response = self.app.get(survey_url)
        self.assertEqual(response.status_code, 302)
        redirect_url = response.location
        parsed_redirect_url = urlparse.urlparse(redirect_url)
        self.assertEqual(parsed_redirect_url.netloc, 'survey.az1.qualtrics.com')
        self.assertEqual(parsed_redirect_url.path, '/SE/')
        parsed_redirect_qs = urlparse.parse_qs(parsed_redirect_url.query)
        self.assertEqual(parsed_redirect_qs['SID'], [self.sid])
        self.assertEqual(parsed_redirect_qs['user_key'], [user_key])
        self.assertEqual(parsed_redirect_qs['variant'], ['n'])

    def test_share_link(self):
        Event.objects.all().delete()
        response = self.app.get(self.url + '?variant=n&g=f&agroup=over&utm_expid=56789')
        event = Event.objects.get(
            variant='n',
            category='page',
            action='view',
            label=self.data['pageview_label'])
        user_key = re.search(r'^\d+$', event.user_key).group()
        extra_data = json.loads(event.extra_data)
        self.assertEqual('f', extra_data['g'])
        self.assertEqual('over', extra_data['agroup'])
        # Try the Facebook link first:
        share_url = response.html.find('a', {'id': 'share-facebook'})['href']
        parsed_url = urlparse.urlparse(share_url)
        self.assertEqual(parsed_url.path,
                         reverse(self.data['base_view_name'] + '-share'))
        self.assertEqual(parsed_url.query,
                         'n=facebook')
        # Now follow that link to find the redirect:
        response = self.app.get(share_url)
        self.assertEqual(response.status_code, 302)
        redirect_url = response.location
        parsed_redirect_url = urlparse.urlparse(redirect_url)
        self.assertEqual(parsed_redirect_url.netloc, 'www.facebook.com')
        self.assertEqual(parsed_redirect_url.path, '/sharer/sharer.php')
        parsed_redirect_qs = urlparse.parse_qs(parsed_redirect_url.query)

        facebook_url = urllib.unquote(parsed_redirect_qs['u'][0])
        parsed_facebook_url = urlparse.urlparse(facebook_url)
        self.assertEqual(parsed_facebook_url.path, self.url)
        self.assertTrue(re.search(r'^via=[a-f0-9]+$', parsed_facebook_url.query))
