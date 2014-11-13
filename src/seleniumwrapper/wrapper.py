# -*- coding: utf-8 -*-

import collections
import inspect
import time
import random
import selenium
from selenium.webdriver import Ie, Opera, Chrome, Firefox, PhantomJS
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        WebDriverException, ElementNotVisibleException,
                                        NoAlertPresentException)
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def create(drivername, *args, **kwargs):
    if not isinstance(drivername, str):
        msg = "drivername should be an instance of string. given {0}".format(type(drivername))
        raise TypeError(msg)
    drivers = {'ie': Ie,
               'opera': Opera,
               'chrome': Chrome,
               'firefox': Firefox,
               'phantomjs': PhantomJS}
    dname = drivername.lower()
    if dname in drivers:
        try:
            return SeleniumWrapper(drivers[dname](*args, **kwargs))
        except Exception as e:
            raise e
    else:
        msg = "".join(("drivername should be one of [IE, Opera, Chrome, Firefox, PhantomJS]",
                       "(case-insentive). given {0}".format(drivername)))
        raise ValueError(msg)


def connect(drivername, executor, custom_capabilities=None, **kwargs):
    if not isinstance(drivername, str):
        msg = "drivername should be an instance of string. given {0}".format(type(drivername))
        raise TypeError(msg)
    if not isinstance(executor, str):
        msg = "executor should be an instance of string. given {0}".format(type(executor))
        raise TypeError(msg)
    if custom_capabilities and not isinstance(custom_capabilities, dict):
        msg = "custom_capabilities should be an instance of dict. given {0}".format(type(custom_capabilities))
        raise TypeError(msg)
    capabilities = {'ie': DesiredCapabilities.INTERNETEXPLORER,
                    'opera': DesiredCapabilities.OPERA,
                    'chrome': DesiredCapabilities.CHROME,
                    'firefox': DesiredCapabilities.FIREFOX,
                    'android': DesiredCapabilities.ANDROID,
                    'phatomjs': DesiredCapabilities.PHANTOMJS}
    dname = drivername.lower()
    if dname in capabilities:
        capability = capabilities[dname]
        custom_capabilities = custom_capabilities or {}
        for key in custom_capabilities:
            capability[key] = custom_capabilities[key]
        driver = selenium.webdriver.Remote(executor, capability, **kwargs)
        try:
            return SeleniumWrapper(driver)
        except Exception as e:
            raise e
    else:
        msg = "".join(("drivername should be one of [IE, Opera, Chrome, Firefox, PhantomJS]",
                       "(case-insentive). given {0}".format(drivername)))
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
                return wrap_or_else(result)

            return reaction
        else:
            return wrap_or_else(methodobj)

    return containment


class Performance(object):
    def __init__(self, performance):
        if not isinstance(performance, dict):
            raise AttributeError('Wrapped performance object should be an instance of dict.')
        self._performance = performance

    @property
    def memory(self):
        if 'memory' in self._performance:
            return Memory(self._performance['memory'])
        raise AttributeError('window.performance.memory is not supported in this browser.')

    @property
    def navigation(self):
        if 'navigation' in self._performance:
            return Navigation(self._performance['navigation'])
        raise AttributeError('window.performance.navigation is not supported in this browser.')

    @property
    def timing(self):
        if 'timing' in self._performance:
            return Timing(self._performance['timing'])
        raise AttributeError('window.performance.timing is not supported in this browser.')


class Memory(object):
    def __init__(self, memory):
        self._memory = memory

    def __getattr__(self, name):
        return self._memory[name]

    @property
    def __dict__(self):
        return self._memory

    def __iter__(self):
        return iter(self._memory)


class Navigation(object):
    def __init__(self, navigation):
        self._navigation = navigation

    def __getattr__(self, name):
        return self._navigation[name]

    @property
    def __dict__(self):
        return self._navigation

    def __iter__(self):
        return iter(self._navigation)


class Timing(object):
    def __init__(self, timing):
        self._timing = timing

    def __getattr__(self, name):
        return self._timing[name]

    @property
    def __dict__(self):
        return self._timing

    def __iter__(self):
        return iter(self._timing)


class SeleniumWrapper(object):
    def __init__(self, driver, timeout=5, silent=False):
        if _is_wrappable(driver):
            self._wrapped = driver
            self._timeout = timeout
            self._silent = silent
        else:
            msg = "2nd argument should be an instance of WebDriver or WebElement. given {0}.".format(type(driver))
            raise TypeError(msg)

    @property
    def unwrap(self):
        return self._wrapped

    @property
    def performance(self):
        if isinstance(self._wrapped, WebDriver):
            if self._wrapped.execute_script("return 'performance' in window;"):
                timeout = time.time() + 120
                script = "return window.performance.timing.loadEventEnd;"
                executor = self._wrapped.execute_script
                while time.time() < timeout and not executor(script):
                    time.sleep(0.2)
                if not executor(script):
                    raise Exception('Timeout!')
                performance = self._wrapped.execute_script('return window.performance;')
                return Performance(performance)
            else:
                raise AttributeError("This browser is not supporting Timing APIs.")
        else:
            raise AttributeError("'WebElement' object has not attribute 'performance'")

    @property
    def parent(self):
        if isinstance(self._wrapped, WebElement):
            return self.xpath("./parent::node()", timeout=self._timeout)
        else:
            raise AttributeError("'WebDriver' object has no attribute 'parent'")

    @property
    def to_select(self):
        if self._is_selectable():
            return Select(self.unwrap)
        raise TypeError("Must be 'select' element.")

    @property
    def alert(self):
        timeout = time.time() + self._timeout
        while time.time() < timeout:
            try:
                alert = self._wrapped.switch_to_alert()
                alert.text
                return alert
            except NoAlertPresentException:
                time.sleep(0.2)
        msg = "Wait for alert to be displayed for 2 seconds, but it was not displayed."
        raise NoAlertPresentException(msg)

    def _settimeout(self, timeout):
        if isinstance(timeout, (int, float)):
            self._timeout = timeout
        else:
            raise AttributeError

    def _gettimeout(self):
        return self._timeout

    timeout = property(_gettimeout, _settimeout)

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, true_of_false):
        if not isinstance(true_of_false, bool):
            raise AttributeError
        self._silent = true_of_false

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    @_chainreact
    def __getattr__(self, name):
        return self._wrapped, getattr(self._wrapped, name)

    def _is_selectable(self):
        return self.unwrap.tag_name == 'select'

    def _is_stopping(self, interval):
        before = (self._wrapped.location['x'], self._wrapped.location['y'])
        time.sleep(interval)
        after = (self._wrapped.location['x'], self._wrapped.location['y'])
        return before[0] == after[0] and before[1] == after[1]

    def _wait_until_stopping(self, timeout, interval):
        timeout = time.time() + timeout
        while time.time() < timeout:
            if self._is_stopping(interval):
                return True
            else:
                time.sleep(interval)
        if not self._is_stopping(interval):
            raise WebDriverException("Element was not stably displayed for {sec} seconds.".format(sec=timeout))

    def _wait_until_clickable(self, timeout, interval):
        err_messages = []
        endtime = time.time() + timeout
        while True:
            try:
                self._wrapped.click()
                break
            except WebDriverException as e:
                err_messages.append(e.msg.split(":")[-1].strip())
            time.sleep(interval)
            if (time.time() > endtime):
                if err_messages:
                    template = ("Waited for element to be clickable for {sec} seconds, ",
                                "but clicked other elements. {err}")
                    msg = "".join(template).format(sec=timeout, err=err_messages)
                    raise WebDriverException(msg)

    def _wait_until_displayed(self, timeout, interval):
        try:
            WebDriverWait(self._wrapped, timeout, interval).until(lambda d: d.is_displayed())
        except TimeoutException:
            template = ("Waited for element to be displayed for {sec} seconds, ",
                        "but <{target} ...> was not displayed:: <{dumped}>")
            msg = "".join(template).format(sec=timeout, target=self._wrapped.tag_name, dumped=self._dump())
            raise ElementNotVisibleException(msg)

    def _dump(self):
        element = self._wrapped
        info = {"visibility": element.value_of_css_property("visibility"),
                "display": element.value_of_css_property("display"),
                "height": element.value_of_css_property("height"),
                "width": element.value_of_css_property("width"),
                "x": element.location["x"],
                "y": element.location["y"]}
        dumped = " ".join(["{k}:{v}".format(k=k, v=info[k]) for k in info])
        return dumped

    def attr(self, name):
        if isinstance(self._wrapped, WebElement):
            return self._wrapped.get_attribute(name)
        else:
            raise AttributeError("This is WebDriver wrapped object.")

    def click(self, timeout=None, presleep=0, postsleep=0):
        timeout = timeout or self._timeout
        if isinstance(self._wrapped, WebElement):
            try:
                if presleep:
                    time.sleep(presleep)
                self._wait_until_stopping(timeout, 0.01)
                self._wait_until_displayed(timeout, 0.01)
                self._wait_until_clickable(timeout, 0.01)
                if postsleep:
                    time.sleep(postsleep)
            except Exception as e:
                raise e

    def scroll_to(self, x, y):
        if isinstance(self._wrapped, WebDriver):
            return self._wrapped.execute_script("window.scrollTo({:d}, {:d})".format(x, y))
        else:
            raise AttributeError("This is WebElement wrapped object.")

    def scroll_by(self, x, y):
        if isinstance(self._wrapped, WebDriver):
            return self._wrapped.execute_script("window.scrollBy({:d}, {:d})".format(x, y))
        else:
            raise AttributeError("This is WebElement wrapped object.")

    def scroll_into_view(self, jq_identifier, align_with_top=True):
        if isinstance(self._wrapped, WebDriver):
            if self._wrapped.execute_script("try{return $;}catch(e){}"):
                script_template = "try{{$('{0}') && $('{0}')[0].scrollIntoView({1})}}catch(e){{}}"
                script = script_template.format(jq_identifier, 'true' if align_with_top else 'false')
                self._wrapped.execute_script(script)
            else:
                raise AttributeError("You must load jquery library.")
        else:
            raise AttributeError("This is WebElement wrapped object.")

    def waitfor(self, type, target, eager=False, timeout=None):
        timeout = timeout or self._timeout
        if eager:
            types = {"id": lambda d: d.find_elements_by_id(target),
                     "name": lambda d: d.find_elements_by_name(target),
                     "xpath": lambda d: d.find_elements_by_xpath(target),
                     "link_text": lambda d: d.find_elements_by_link_text(target),
                     "partial_link_text": lambda d: d.find_elements_by_partial_link_text(target),
                     "tag": lambda d: d.find_elements_by_tag_name(target),
                     "class": lambda d: d.find_elements_by_class_name(target),
                     "css": lambda d: d.find_elements_by_css_selector(target), }
        else:
            types = {"id": lambda d: d.find_element_by_id(target),
                     "name": lambda d: d.find_element_by_name(target),
                     "xpath": lambda d: d.find_element_by_xpath(target),
                     "link_text": lambda d: d.find_element_by_link_text(target),
                     "partial_link_text": lambda d: d.find_element_by_partial_link_text(target),
                     "tag": lambda d: d.find_element_by_tag_name(target),
                     "class": lambda d: d.find_element_by_class_name(target),
                     "css": lambda d: d.find_element_by_css_selector(target), }
        finder = types[type]
        try:
            result = WebDriverWait(self._wrapped, timeout).until(finder)
            if eager and len(result):
                return SeleniumContainerWrapper(result, self.timeout, self.silent)
            elif _is_wrappable(result):
                return SeleniumWrapper(result, self.timeout, self.silent)
            else:
                return result
        except TimeoutException:
            if self.silent:
                return None
            else:
                template = ("Waited for element to appear for {sec} seconds, ",
                            "but {type}:{target} didn't appear.")
                msg = "".join(template).format(sec=timeout, type=type, target=target)
                raise NoSuchElementException(msg)

    def xpath(self, target, eager=False, timeout=None):
        return self.waitfor("xpath", target, eager, timeout)

    def css(self, target, eager=False, timeout=None):
        return self.waitfor("css", target, eager, timeout)

    def by_tag(self, tag, eager=False, timeout=None, **attributes):
        subjects = ["@{key}='{val}'".format(key=k, val=attributes[k]) for k in attributes]
        subject = " and ".join(subjects)
        xpath = ".//{tag}[{subject}]".format(tag=tag, subject=subject) if subject else ".//{tag}".format(tag=tag)
        return self.waitfor('xpath', xpath, eager, timeout)

    def by_text(self, text, tag="*", partial=False, eager=False, timeout=None):
        if partial:
            return self.xpath(".//{tag}[contains(text(), '{text}')]".format(tag=tag, text=text), eager, timeout)
        return self.xpath(".//{tag}[text()='{text}']".format(tag=tag, text=text), eager, timeout)

    def by_class(self, target, eager=False, timeout=None):
        return self.waitfor("class", target, eager, timeout)

    def by_id(self, target, eager=False, timeout=None):
        return self.waitfor("id", target, eager, timeout)

    def by_name(self, target, eager=False, timeout=None):
        return self.waitfor("name", target, eager, timeout)

    def by_linktxt(self, target, eager=False, timeout=None, partial=False):
        if partial:
            return self.waitfor("partial_link_text", target, eager, timeout=None)
        else:
            return self.waitfor("link_text", target, eager, timeout)

    def href(self, partialurl=None, eager=False, timeout=None):
        if partialurl:
            return self.xpath(".//a[contains(@href, '{0}')]".format(partialurl), eager, timeout)
        return self.xpath(".//a", eager, timeout)

    def img(self, alt=None, ext=None, eager=False, timeout=None):
        options = []
        if alt:
            options.append("@alt='{0}'".format(alt))
        if ext:
            options.append("contains(@src, '{0}')".format(ext))
        option = " and ".join(options)
        xpath = ".//img" + "[{0}]".format(option) if option else ".//img"
        return self.xpath(xpath, eager, timeout)

    def button(self, value, eager=False, timeout=None):
        return self.xpath(
            ".//input[@type='submit' or @type='button' and @value='{0}']"
            "|.//button[text()='{0}']".format(value), eager, timeout)

    def checkbox(self, eager=False, timeout=None, **attributes):
        attributes["type"] = "checkbox"
        return self.by_tag("input", eager, timeout, **attributes)

    def radio(self, eager=False, timeout=None, **attributes):
        attributes["type"] = "radio"
        return self.by_tag("input", eager, timeout, **attributes)

    def select(self, eager=False, timeout=None, **attributes):
        selected = self.by_tag("select", eager, timeout, **attributes)
        if isinstance(selected, SeleniumWrapper) and selected._is_selectable():
            return Select(selected.unwrap)
        elif isinstance(selected, SeleniumContainerWrapper):
            iterable = selected._iterable
            selected._iterable = [Select(element) for element in iterable if element.tag_name == 'select']
            return selected
        else:
            template = ("Waited for element to appear for {sec} seconds, ",
                        "but select:{attr} didn't appear.")
            msg = "".join(template).format(sec=timeout, attr=attributes)
            raise NoSuchElementException(msg)


class SeleniumContainerWrapper(object):
    def __init__(self, iterable, timeout=5, silent=False):
        if not isinstance(iterable, collections.Sequence):
            msg = "2nd argument should be an instance of collections.Sequence. given {0}".format(type(iterable))
            raise TypeError(msg)
        self._iterable = iterable
        self._timeout = timeout
        self._silent = silent

    @_chainreact
    def __getattr__(self, name):
        """Wrap return value using '_chanreact'."""
        return self._iterable, getattr(self._iterable, name)

    def __getitem__(self, key):
        obj = self._iterable[key]
        if _is_wrappable(obj):
            return SeleniumWrapper(obj, self._timeout, self._silent)
        return obj

    def __len__(self):
        return len(self._iterable)

    def __contains__(self, key):
        key = key.unwrap if isinstance(key, SeleniumWrapper) else key
        return key in self._iterable

    @property
    def size(self):
        return len(self._iterable)

    def sample(self, size):
        picked = random.sample(self._iterable, size)
        if isinstance(picked, collections.Sequence):
            return SeleniumContainerWrapper(picked, self._timeout, self._silent)
        return picked

    def choice(self):
        picked = random.choice(self._iterable)
        if _is_wrappable(picked):
            return SeleniumWrapper(picked, self._timeout, self._silent)
        else:
            return picked
