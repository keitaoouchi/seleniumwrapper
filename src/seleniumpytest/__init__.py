# -*- coding: utf-8 -*-

__all__ = ["SeleniumWrapper"]

import selenium
from selenium.webdriver.support.ui import WebDriverWait
import unittest, functools

def _wrappable(obj):
    if (isinstance(obj, selenium.webdriver.remote.webdriver.WebDriver) or
        isinstance(obj, selenium.webdriver.remote.webelement.WebElement)):
        return True
    else:
        return False

def _chainreact(__getattr__):
    """Decorator function used in Chainable's __getattr__ method.
    
    Chainable object support methods of its wrapped objects, and try to keep
    its return value also chainable.
    """
    def containment(*methodname):
        self, methodobj = __getattr__(*methodname)
        def reaction(*realargs):
            result = methodobj(*realargs)
            result = result if result else self
            if _wrappable(result):
                return SeleniumWrapper(result)
            else:
                return result
        return reaction
    return containment

class SeleniumWrapper(object):

    def __init__(self, driver):
        if _wrappable(driver):
            self._driver = driver
        else:
            raise Exception()

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    @_chainreact
    def __getattr__(self, name):
        return self._driver, getattr(self._driver, name)

    def wait_and_get(self, type, target, timeout=10):
        types = {"id":lambda d: d.find_element_by_id(target),
                 "name":lambda d: d.find_element_by_name(target),
                 "xpath":lambda d: d.find_element_by_xpath(target),
                 "link_text":lambda d: d.find_element_by_link_text(target),
                 "partial_link_text":lambda d: d.find_element_by_partial_link_text(target),
                 "tag":lambda d: d.find_element_by_tag_name(target),
                 "class":lambda d: d.find_element_by_class_name(target),
                 "css":lambda d: d.find_element_by_css_selector(target), }
        finder = types[type]
        return WebDriverWait(self._driver, timeout).until(finder)


