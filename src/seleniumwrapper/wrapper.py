# -*- coding: utf-8 -*-

import collections
import inspect
from selenium.webdriver import Ie, Opera, Chrome, Firefox
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

def create(drivername):
    if not isinstance(drivername, str):
        msg = "drivername should be an instance of string. given {0}".format(type(drivername))
        raise TypeError(msg)
    drivers = {'ie': Ie,
               'opera': Opera,
               'chrome': Chrome,
               'firefox': Firefox}
    dname = drivername.lower()
    if dname in drivers:
        try:
            return SeleniumWrapper(drivers[dname]())
        except Exception, e:
            raise e
    else:
        msg = "drivername should be one of [IE, Opera, Chrome, Firefox](case-insentive). given {0}".format(drivername)
        raise ValueError(msg)

def _is_wrappable(obj):
    if isinstance(obj, WebDriver) or isinstance(obj, WebElement):
        return True
    else:
        return False

def _chainreact(__getattr__):
    def containment(*methodname):
        def wrap_or_else(obj):
            if _is_wrappable(obj):
                return SeleniumWrapper(obj)
            else:
                return obj
        self, methodobj = __getattr__(*methodname)
        if inspect.isroutine(methodobj):
            def reaction(*realargs):
                result = methodobj(*realargs)
                # for side-effective method(append, ...)
                result = result if result else self
                return wrap_or_else(result)
            return reaction
        else:
            return wrap_or_else(methodobj)
    return containment

class SeleniumWrapper(object):

    def __init__(self, driver):
        if _is_wrappable(driver):
            self._driver = driver
        else:
            msg = "2nd argument should be an instance of WebDriver or WebElement. given {0}.".format(type(driver))
            raise TypeError(msg)

    @property
    def unwrap(self):
        return self._driver

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    @_chainreact
    def __getattr__(self, name):
        return self._driver, getattr(self._driver, name)

    def _is_selectable(self):
        return self.unwrap.tag_name == u'select'

    def waitfor(self, type, target, eager=False, timeout=10):
        if eager:
            types = {"id":lambda d: d.find_elements_by_id(target),
                     "name":lambda d: d.find_elements_by_name(target),
                     "xpath":lambda d: d.find_elements_by_xpath(target),
                     "link_text":lambda d: d.find_elements_by_link_text(target),
                     "partial_link_text":lambda d: d.find_elements_by_partial_link_text(target),
                     "tag":lambda d: d.find_elements_by_tag_name(target),
                     "class":lambda d: d.find_elements_by_class_name(target),
                     "css":lambda d: d.find_elements_by_css_selector(target), }
        else:
            types = {"id":lambda d: d.find_element_by_id(target),
                     "name":lambda d: d.find_element_by_name(target),
                     "xpath":lambda d: d.find_element_by_xpath(target),
                     "link_text":lambda d: d.find_element_by_link_text(target),
                     "partial_link_text":lambda d: d.find_element_by_partial_link_text(target),
                     "tag":lambda d: d.find_element_by_tag_name(target),
                     "class":lambda d: d.find_element_by_class_name(target),
                     "css":lambda d: d.find_element_by_css_selector(target), }
        finder = types[type]
        result = WebDriverWait(self._driver, timeout).until(finder)
        if eager and len(result):
            return SeleniumContainerWrapper(result)
        elif _is_wrappable(result):
            return SeleniumWrapper(result)
        else:
            return result

    def xpath(self, target, eager=False, timeout=10):
        return self.waitfor("xpath", target, eager, timeout)

    def css(self, target, eager=False, timeout=10):
        return self.waitfor("css", target, eager, timeout)

    def tag(self, target, eager=False, timeout=10):
        return self.waitfor("tag", target, eager, timeout)

    def by_class(self, target, eager=False, timeout=10):
        return self.waitfor("class", target, eager, timeout)

    def by_id(self, target, eager=False, timeout=10):
        return self.waitfor("id", target, eager, timeout)

    def by_name(self, target, eager=False, timeout=10):
        return self.waitfor("name", target, eager, timeout)

    def by_linktxt(self, target, eager=False, timeout=10, partial=False):
        if partial:
            return self.waitfor("partial_link_text", target, eager, timeout=10)
        else:
            return self.waitfor("link_text", target, eager, timeout)

    def href(self, partialurl=None, eager=False, timeout=10):
        if partialurl:
            return self.xpath("//a[contains(@href, '{0}')]".format(partialurl), eager, timeout)
        return self.xpath("//a", eager, timeout)

    def img(self, eager=True, ext=None, timeout=10):
        if ext:
            return self.xpath("//img[contains(@src, '{0}')]".format(ext), eager, timeout)
        return self.xpath("//img", eager, timeout)

    @property
    def select(self):
        if self._is_selectable():
            return Select(self.unwrap)
        return None

class SeleniumContainerWrapper(object):

    def __init__(self, iterable):
        if not isinstance(iterable, collections.Sequence):
            msg = "2nd argument should be an instance of collections.Sequence. given {0}".format(type(iterable))
            raise TypeError(msg)
        self._iterable = iterable

    @_chainreact
    def __getattr__(self, name):
        """Wrap return value using '_chanreact'."""
        return self._iterable, getattr(self._iterable, name)

    def __getitem__(self, key):
        obj = self._iterable[key]
        if _is_wrappable(obj):
            return SeleniumWrapper(obj)
        return obj

    def __len__(self):
        return len(self._iterable)

    def __contains__(self, key):
        return key in self._iterable
