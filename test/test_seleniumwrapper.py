import sys

sys.path.append("./../src")

import unittest
import mock
import seleniumwrapper
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumwrapper.wrapper import SeleniumWrapper
from seleniumwrapper.wrapper import SeleniumContainerWrapper
from selenium.common.exceptions import TimeoutException

class TestSeleniumWrapper(unittest.TestCase):

    def test_init_raise_if_driver_is_not_a_webdriver_object(self):
        self.assertRaises(TypeError, SeleniumWrapper, 'hoge')

    def test_init_not_raise_if_driver_is_a_webdriver_object(self):
        mocked_driver = mock.Mock(WebDriver)
        SeleniumWrapper(mocked_driver)

    def test_wrapper_should_delegate_unknown_attribute_access_to_wrapped_driver(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_driver.hoge = lambda d: d
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.hoge(1), 1)

    def test_wrapper_should_raise_AttributeError_if_wrapped_driver_also_dont_have_attribute_with_given_name(self):
        mocked_driver = mock.Mock(WebDriver)
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertRaises(AttributeError, getattr, *[wrapper, 'hoge'])

    def test_wrapper_should_chain_wrapping_if_possible(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_element = mock.Mock(WebElement)
        mocked_driver.find_element_by_id = lambda given: given
        wrapper = SeleniumWrapper(mocked_driver)
        wrapped_element = wrapper.find_element_by_id(mocked_element)
        unwrapped_element = wrapper.find_element_by_id("hoge")
        self.assertTrue(isinstance(wrapped_element, SeleniumWrapper))
        self.assertFalse(isinstance(unwrapped_element, SeleniumWrapper))

    def test_wrapper_should_respond_to_waitfor(self):
        mocked_driver = mock.Mock(WebDriver)
        mocked_driver.find_element_by_id = lambda target: target
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.waitfor('id', 'hoge'), 'hoge')

    def test_create_raise_typeerror_if_argument_is_not_a_string(self):
        self.assertRaises(TypeError, seleniumwrapper.create, 1)

    def test_create_raise_valueerror_if_argument_is_invalid_drivername(self):
        self.assertRaises(ValueError, seleniumwrapper.create, 'Chorome')
        self.assertRaises(ValueError, seleniumwrapper.create, 'Firedog')

    def test_wrapper_should_handle_attr_access_even_if_attr_is_descriptor(self):
        mocked_element = mock.Mock(WebElement)
        class Hoge(WebDriver):
            def __init__(self):
                pass
            @property
            def hoge(self):
                return mocked_element
            @property
            def num(self):
                return 100
        mocked_driver = Hoge()
        wrapper = SeleniumWrapper(mocked_driver)
        self.assertEquals(wrapper.num, 100)
        self.assertTrue(isinstance(wrapper.hoge, SeleniumWrapper), wrapper.hoge)

class TestSeleniumWrapperAliases(unittest.TestCase):

    def setUp(self):
        mocky = mock.Mock(WebDriver)
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
        mock_elem = mock.Mock(WebElement)
        self.mock.find_element_by_xpath.return_value = mock_elem
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy"), SeleniumWrapper)

    def test_waitfor_wraps_its_return_value_if_given_eager_arument_is_true(self):
        mock_elem = mock.Mock(WebElement)
        self.mock.find_elements_by_xpath.return_value = [mock_elem]
        wrapper = SeleniumWrapper(self.mock)
        self.assertIsInstance(wrapper.waitfor("xpath", "dummy", eager=True), SeleniumContainerWrapper)

    def test_aliases_work_collectly(self):
        mock_elem = mock.Mock(WebElement)
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
    suite.addTests(unittest.makeSuite(TestSeleniumWrapperAliases))
    suite.addTests(unittest.makeSuite(TestSeleniumWrapper))
    return suite

if __name__ == "__main__":
    suite()
