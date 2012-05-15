About this module
-----------------
selenium webdriver wrapper to make manipulation easier. 

How to install
--------------
Requires python2.6 or later (include python3.x).
You need *pip* or *distribute* or *setuptools*::

    $ pip install seleniumwrapper

or use easy_install::

    $ easy_install seleniumwrapper

also you need selenium::

    $ pip install selenium
    
Example to use::
----------------

    >>> import seleniumwrapper as selwrap
    >>> br = selwrap.create("chrome")
    # SeleniumWrapper delegate to its wrapped webdriver.
    >>> br.get("http://www.example.com")
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>
    >>> br.xpath("//div[@class='main'])
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>
    # set eager=True => find_elements_by
    >>> br.xpath("//a", eager=True)
    <seleniumwrapper.wrapper.SeleniumContainerWrapper object at 0x...>
    # SeleniumContainerWrapper also delegate to its wrapped container.
    >>> links = [i.get_attribute("href") for i in br.xpath("//a", eager=True)]
    # each content in SeleniumContainerWrapper also SeleniumWrapper.
    >>> tds = [tr.xpath("//td", eager=True) for tr in br.xpath("//tr", eager=True)]
    
Basic API
---------
* seleniumwrapper.create(drivername)
    Create webdriver instance and wrap it with SeleniumWrapper.

SeleniumWrapper
^^^^^^^^^^^^^^^
* unwrap
    Retrieves WebDriver or WebElement from wrapped object.
* waitfor(type, target, eager=False, timeout=10)
    See source.
* xpath(target, eager=False, timeout=10)
    find_element_by_xpath(target, timeout)
* css(target, eager=False, timeout=10)
    find_element_by_css_selector(target, timeout)
* tag(target, eager=False, timeout=10)
    find_element_by_tag_name(target, timeout)
* by_class(target, eager=False, timeout=10)
    find_element_by_class_name(target, timeout)
* by_id(target, eager=False, timeout=10)
    find_element_by_id(target, timeout)
* by_name(target, eager=False, timeout=10)
    find_element_by_name(target, timeout)
* by_linktxt(target, eager=False, timeout=10, partial=False)
    find_element_by_link_text(target, timeout). if partial=True, then find_element_by_partial_link_text
* href(url, eager=False, timeout=10):
    find_element_by_xpath("//a[@href='%s']".format(url), timeout)
* img(eager=True, ext=None, timeout=10)
    find_elements_by_xpath("//img", timeout). 