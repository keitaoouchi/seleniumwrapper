About this module
-----------------
selenium webdriver wrapper to make manipulation easier.

Features
--------

* Easy to type aliases. (find_element_by_xpath => xpath, etc.)
* Wrapped WebdriverWait( ... ).until( ... ) pattern.
* Polling at the time of clicking or selecting.
* Wrapping chaining.

How to install
--------------
Requires python2.6 or later (exclude python3.x).
You need *pip* or *distribute* or *setuptools*::

    $ pip install seleniumwrapper

or use easy_install::

    $ easy_install seleniumwrapper

also you need selenium::

    $ pip install selenium

Example to use
--------------

*create* function helps you to init webdriver and wrap it easily::

    >>> import seleniumwrapper as selwrap
    >>> br = selwrap.create("chrome")

SeleniumWrapper delegate to its wrapped webdriver::

    >>> br.get("http://www.example.com")
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>
    >>> br.xpath("//div[@class='main'])
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>

Setting *eager=True* to invoke find_elements::

    >>> br.xpath("//a", eager=True)
    <seleniumwrapper.wrapper.SeleniumContainerWrapper object at 0x...>

SeleniumContainerWrapper also delegate to its wrapped container::

    >>> links = [i.get_attribute("href") for i in br.xpath("//a", eager=True)]

Each contents in SeleniumContainerWrapper also SeleniumWrapper::

    >>> tds = [tr.xpath("//td", eager=True) for tr in br.xpath("//tr", eager=True)]

Basic API
---------
* seleniumwrapper.create(drivername)
    Create webdriver instance and wrap it with SeleniumWrapper.

SeleniumWrapper
^^^^^^^^^^^^^^^
* unwrap
    Retrieves WebDriver or WebElement from wrapped object.
* parent
    find_element_by_xpath("./parent::node()")
* select
    Return Select(self.unwrap) if possible, else return None.
* click(timeout=3, presleep=0, postsleep=0)
    Continue to polling until timeout or element is displayed and clickable.
* waitfor(type, target, eager=False, timeout=3)
    See source.
* xpath(target, eager=False, timeout=3)
    find_element_by_xpath(target, timeout)
* css(target, eager=False, timeout=3)
    find_element_by_css_selector(target, timeout)
* tag(target, eager=False, timeout=3)
    find_element_by_tag_name(target, timeout)
* by_text(text, tag='*', partial=False, eager=False, timeout=3)
    similar to find_element_by_link_text or find_element_by_partial_link_text, but this method can be applicable to any tag.
* by_class(target, eager=False, timeout=3)
    find_element_by_class_name(target, timeout)
* by_id(target, eager=False, timeout=3)
    find_element_by_id(target, timeout)
* by_name(target, eager=False, timeout=3)
    find_element_by_name(target, timeout)
* by_linktxt(target, eager=False, timeout=3, partial=False)
    find_element_by_link_text(target, timeout). if partial=True, then find_element_by_partial_link_text
* href(partialurl=None, eager=False, timeout=3):
    find_element_by_xpath("//a", timeout). if partialurl was given, search 'a' tag which href contains partialurl.
* img(eager=True, ext=None, timeout=3)
    find_elements_by_xpath("//img", timeout).
* button(value, eager=False, timeout=3)
    find_element_by_xpath("//input[@type='submit' and @value='{}']".format(value), timeout)

Recent Change
------------
* 0.2.2
    * Add new property *alert*
    * Change *img*'s argument from ext to alt( find_element_by_xpath("//img[@alt='{}'.format(alt)) )
    * Modify SeleniumContainerWrapper's __contains__ behavior to unwrap given object if it is a SeleniumWrapper.
