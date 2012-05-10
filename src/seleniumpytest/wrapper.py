# -*- coding: utf-8 -*-

import selenium
from selenium.webdriver.support.ui import WebDriverWait

def _wrappable(obj):
    if (isinstance(obj, selenium.webdriver.remote.webdriver.WebDriver) or
        isinstance(obj, selenium.webdriver.remote.webelement.WebElement)):
        return True
    else:
        return False

def _chainreact(__getattr__):
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
            msg = "2nd argument should be an instance of WebDriver or WebElement. Given %s.".format(type(driver))
            raise TypeError(msg)

    @classmethod
    def create(cls, drivername):
        drivers = {'ie': selenium.webdriver.Ie,
                   'opera': selenium.webdriver.Opera,
                   'chrome': selenium.webdriver.Chrome,
                   'firefox': selenium.webdriver.Firefox}
        if not isinstance(drivername, str):
            msg = "drivername should be an instance of string. given %s".format(type(drivername))
            raise TypeError(msg)
        dname = drivername.lower()
        if dname in drivers:
            try:
                driver = drivers[dname]()
                return driver
            except Exception, e:
                raise e
        else:
            msg = "drivername should be one of [IE, Opera, Chrome, Firefox](case-insentive). given %s".format(drivername)
            raise ValueError(msg)

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


