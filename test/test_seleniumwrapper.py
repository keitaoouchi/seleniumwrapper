import sys

sys.path.append("./../src")

import unittest
import selenium
import mock
from seleniumpytest.wrapper import SeleniumWrapper

class TestSeleniumWrapper(unittest.TestCase):

    def test_init_raise_if_driver_is_not_a_webdriver_object(self):
        self.assertRaises(TypeError, SeleniumWrapper, 'hoge')

    def test_init_not_raise_if_driver_is_a_webdriver_object(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        SeleniumWrapper(mocked_driver)

    def test_wrapper_should_delegate_unknown_attribute_access_to_wrapped_driver(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        mocked_driver.hoge = lambda d: d
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.hoge(1), 1)

    def test_wrapper_should_raise_AttributeError_if_wrapped_driver_also_dont_have_attribute_with_given_name(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertRaises(AttributeError, getattr, *[wrapper, 'hoge'])

    def test_wrapper_should_chain_wrapping_if_possible(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        mocked_element = mock.Mock(selenium.webdriver.remote.webelement.WebElement)
        mocked_driver.find_element_by_id = lambda given: given
        wrapper = SeleniumWrapper(mocked_driver)
        wrapped_element = wrapper.find_element_by_id(mocked_element)
        unwrapped_element = wrapper.find_element_by_id("hoge")
        self.assertTrue(isinstance(wrapped_element, SeleniumWrapper))
        self.assertFalse(isinstance(unwrapped_element, SeleniumWrapper))

    def test_wrapper_should_respond_to_waitfor(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        mocked_driver.find_element_by_id = lambda target: target
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.waitfor('id', 'hoge'), 'hoge')

    def test_create_raise_typeerror_if_argument_is_not_a_string(self):
        self.assertRaises(TypeError, SeleniumWrapper.create, 1)

    def test_create_raise_valueerror_if_argument_is_invalid_drivername(self):
        self.assertRaises(ValueError, SeleniumWrapper.create, 'Chorome')
        self.assertRaises(ValueError, SeleniumWrapper.create, 'Firedog')

class TestSeleniumWrappersTanpopoWork(unittest.TestCase):

    def setUp(self):
        mocky = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        mock.find_element_by_id = lambda t: t
        mock.find_element_by_name = lambda t: t
        mock.find_element_by_xpath = lambda t: t
        mock.find_element_by_link_text = lambda t: t
        mock.find_element_by_partial_link_text = lambda t: t
        mock.find_element_by_tag_name = lambda t: t
        mock.find_element_by_class_name = lambda t: t
        mock.find_element_by_css_selector = lambda t: t
        # tanpopo work!
        mock.find_elements_by_id = lambda t: [t]
        mock.find_elements_by_name = lambda t: [t]
        mock.find_elements_by_xpath = lambda t: [t]
        mock.find_elements_by_link_text = lambda t: [t]
        mock.find_elements_by_partial_link_text = lambda t: [t]
        mock.find_elements_by_tag_name = lambda t: [t]
        mock.find_elements_by_class_name = lambda t: [t]
        mock.find_elements_by_css_selector = lambda t: [t]
        self.mock = mocky

    def test_waitfor(self):
        wrapper = SeleniumWrapper(self.mock)
        self.assertTrue(hasattr(wrapper, 'waitfor'))
        self.assertEquals(wrapper.waitfor("xpath", "hoge"), "hoge")
        self.assertEquals(wrapper.waitfor("xpath", "hoge", eager=True), ["hoge"])

    def test_xpath(self):
        """
        wrapper = SeleniumWrapper(self.mock)
        self.assertTrue(hasattr(wrapper, 'xpath'))
        self.assertEquals(wrapper.xpath("hoge"), "hoge")
        self.assertEquals(wrapper.xpath("hoge", eager=True), ["hoge"])
        """
        pass

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestSeleniumWrapperTanpopoWork))
    return suite

if __name__ == "__main__":
    suite()
