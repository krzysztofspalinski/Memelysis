from django.test import LiveServerTestCase
from selenium import webdriver
from time import time

# Create your tests here.


class AnonymousUserTests(LiveServerTestCase):

	fixtures = ['functional_tests/fixtures.json']

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()

	def test_index_page_loading_time(self):
		start_time = time()
		self.browser.get(self.live_server_url)
		self.assertLess(time()-start_time, 10)

	def test_images_are_displayed_correctly(self):
		self.browser.get(self.live_server_url)
		images = self.browser.find_elements_by_css_selector('img')
		for image in images:
			self.assertTrue(
				self.browser.execute_script(
					"return arguments[0].complete && typeof arguments[0].naturalWidth != \"undefined\" && arguments[0].naturalWidth > 0", image)
			)
