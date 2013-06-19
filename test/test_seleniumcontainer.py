import sys

sys.path.append("./../src")
if sys.version < '2.7':
    import unittest2 as unittest
else:
    import unittest
import collections
import mock
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumwrapper.wrapper import SeleniumWrapper, SeleniumContainerWrapper


class TestSeleniumContainerWrapper(unittest.TestCase):
    def test_container_raise_if_given_argument_is_not_an_instance_of_Sequence(self):
        containment = 1
        self.assertNotIsInstance(containment, collections.Sequence)
        self.assertRaises(TypeError, SeleniumContainerWrapper, containment)

    def test_container_holds_given_argument_if_it_is_an_instance_of_Sequence(self):
        containment = []
        self.assertIsInstance(containment, collections.Sequence)
        SeleniumContainerWrapper(containment)

    def test_container_should_delegate_unknown_attribute_access_to_wrapped_container(self):
        container = SeleniumContainerWrapper([])
        container.append(1)
        container.append(1)
        self.assertEqual(container.count(1), 2)
        self.assertEqual(container.pop(), 1)
        self.assertEqual(container.count(1), 1)

    def test_container_should_return_wrapped_object_if_possible(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2]
        container = SeleniumContainerWrapper(iterable)
        wrapped1 = container.pop()
        self.assertTrue(isinstance(wrapped1, SeleniumWrapper))
        self.assertTrue(hasattr(wrapped1, 'waitfor'))
        wrapped2 = container.pop()
        self.assertTrue(isinstance(wrapped2, SeleniumWrapper))
        self.assertTrue(hasattr(wrapped2, 'waitfor'))

    def test_container_should_support_indexing_and_also_wrap_if_possible(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2, 1]
        container = SeleniumContainerWrapper(iterable)
        self.assertIsInstance(container[0], SeleniumWrapper)
        self.assertIsInstance(container[1], SeleniumWrapper)
        self.assertIsInstance(container[2], int)

    def test_container_support_for_statement(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2]
        container = SeleniumContainerWrapper(iterable)
        for m in container:
            self.assertIsInstance(m, SeleniumWrapper)

    def test_container_has_length(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2]
        container = SeleniumContainerWrapper(iterable)
        self.assertEqual(len(container), 2)

    def test_container_has_size_property(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2]
        container = SeleniumContainerWrapper(iterable)
        self.assertEqual(container.size, 2)

    def test_container_support__contains__protocol(self):
        mock1 = mock.Mock(WebDriver)
        mock2 = mock.Mock(WebElement)
        iterable = [mock1, mock2]
        container = SeleniumContainerWrapper(iterable)
        self.assertTrue(mock1 in container)
        self.assertTrue(mock2 in container)

    def test_container_unwrap_given_object_if_possible_in__contains__protocol(self):
        mocked = mock.Mock(WebElement)
        iterable = [mocked]
        container = SeleniumContainerWrapper(iterable)
        self.assertTrue(container[0] in container)

    def test_sample_returns_random_sample_from_its_wrapped_iterable(self):
        iterable = [mock.Mock(WebElement) for i in range(10)]
        container = SeleniumContainerWrapper(iterable)
        sampled = container.sample(5)
        self.assertTrue(isinstance(sampled, SeleniumContainerWrapper))
        self.assertEqual(len(sampled), 5)
        for sample in sampled:
            self.assertTrue(sample in container)

    def test_choice_returns_random_choice_from_its_wrapped_iterable(self):
        iterable = [mock.Mock(WebElement) for i in range(10)]
        container = SeleniumContainerWrapper(iterable)
        picked = container.choice()
        self.assertTrue(isinstance(picked, SeleniumWrapper))
        self.assertTrue(picked in container)

    def test_contained_object_inherits_option_properties_from_container(self):
        iterable = [mock.Mock(WebElement) for i in range(5)]
        container = SeleniumContainerWrapper(iterable, 1, True)
        for contained in container:
            self.assertEqual(contained.timeout, 1)
            self.assertTrue(contained.silent)
        self.assertEqual(container[-1].timeout, 1)
        self.assertTrue(container[-1].silent)

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestSeleniumContainerWrapper))
    return suite


if __name__ == "__main__":
    s = suite()
    unittest.TextTestRunner(verbosity=2).run(s)
