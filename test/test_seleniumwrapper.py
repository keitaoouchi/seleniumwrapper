import sys

sys.path.append("./../src")

import unittest
import selenium
import mock
from seleniumpytest.wrapper import SeleniumWrapper, SeleniumContainerWrapper
from selenium.common.exceptions import TimeoutException

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
        self.mock = mocky

    def test_waitfor_raise_if_find_element_return_falsy_value(self):
        self.mock.find_element_by_xpath.return_value = None
        wrapper = SeleniumWrapper(self.mock)
        self.assertRaises(TimeoutException, wrapper.waitfor, *['xpath', 'dummy'], **{'timeout':0.1})
        
    def test_waitfor_raise_if_find_elements_return_falsy_value(self):
        self.mock.find_elements_by_xpath.return_value = []
        wrapper = SeleniumWrapper(self.mock)
        self.assertRaises(TimeoutException, wrapper.waitfor, *['xpath', 'dummy'], **{'eager':True, 'timeout':0.1})
        
    def test_waitfor_wraps_its_return_value_if_it_is_wrappable(self):
        mock_elem = mock.Mock(selenium.webdriver.remote.webdriver.WebElement)
        self.mock.find_element_by_xpath.return_value = mock_elem
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy"), SeleniumWrapper)
        
    def test_waitfor_wraps_its_return_value_if_given_eager_arument_is_true(self):
        mock_elem = mock.Mock(selenium.webdriver.remote.webdriver.WebElement)
        self.mock.find_elements_by_xpath.return_value = [mock_elem]
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy", eager=True), SeleniumContainerWrapper)
        
    def test_aliases_work_collectly(self):
        mock_elem = mock.Mock(selenium.webdriver.remote.webdriver.WebElement)
        self.mock.find_element_by_xpath.return_value = mock_elem
        self.mock.find_element_by_css_selector.return_value = mock_elem
        self.mock.find_element_by_tag_name.return_value = mock_elem
        self.mock.find_element_by_class_name.return_value = mock_elem
        self.mock.find_element_by_id.return_value = mock_elem
        self.mock.find_element_by_name.return_value = mock_elem
        self.mock.find_element_by_link_text.return_value = mock_elem
        self.mock.find_element_by_partial_link_text.return_value = mock_elem
        wrapper = SeleniumWrapper(self.mock)
        
        self.assertIsInstance(wrapper.xpath("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.css("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.tag("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_class("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_id("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_name("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_linktxt("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.by_linktxt("dummy", partial=True), SeleniumWrapper)
        self.assertIsInstance(wrapper.href("dummy"), SeleniumWrapper)
        self.assertIsInstance(wrapper.img(eager=False), SeleniumWrapper)
        

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestSeleniumWrappersTanpopoWork))
    suite.addTests(unittest.makeSuite(TestSeleniumWrapper))
    return suite

if __name__ == "__main__":
    suite()
