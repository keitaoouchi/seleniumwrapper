import sys, os

sys.path.append("./../src")

import unittest
import selenium
import mock
from seleniumwrapper import SeleniumWrapper

class TestSeleniumWrapper(unittest.TestCase):

    def test_init_raise_if_driver_is_not_a_webdriver_object(self):
        self.assertRaises(Exception, SeleniumWrapper, ['hoge'])

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

    def test_wrapper_should_respond_to_wait_and_get(self):
        mocked_driver = mock.Mock(selenium.webdriver.remote.webdriver.WebDriver)
        mocked_driver.find_element_by_id = lambda target: target
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.wait_and_get('id', 'hoge'), 'hoge')

if __name__ == "__main__":
    unittest.main()
