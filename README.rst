About this module
-----------------
selenium webdriver wrapper to make manipulation easier.

.. image:: https://secure.travis-ci.org/keitaoouchi/seleniumwrapper.png

Features
--------

* Support Internet Explorer, Chrome, Opera, Firefox, PhantomJS
* Support remote webdriver.
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

**create** function helps you to init webdriver and wrap it easily::

    >>> import seleniumwrapper as selwrap
    >>> br = selwrap.create("chrome")

**connect** function helps you to use remote webdriver and wrap it::

    >>> br = connect("android", "http://localhost:9999", {"acceptSslCerts": True})

SeleniumWrapper delegate to its wrapped webdriver::

    >>> br.get("http://www.example.com")
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>
    >>> br.xpath("//div[@class='main'])
    <seleniumwrapper.wrapper.SeleniumWrapper object at 0x...>

Setting **eager=True** to invoke find_elements::

    >>> br.xpath("//a", eager=True)
    <seleniumwrapper.wrapper.SeleniumContainerWrapper object at 0x...>

SeleniumContainerWrapper also delegate to its wrapped container::

    >>> links = [i.get_attribute("href") for i in br.xpath("//a", eager=True)]

Each contents in SeleniumContainerWrapper also SeleniumWrapper::

    >>> tds = [tr.xpath("//td", eager=True) for tr in br.xpath("//tr", eager=True)]

Basic API
---------
* seleniumwrapper.create(drivername)
* seleniumwrapper.connect(drivername, executor, custom_capabilities)
    Create webdriver instance and wrap it with SeleniumWrapper.

SeleniumWrapper
^^^^^^^^^^^^^^^
* unwrap
    Retrieves WebDriver or WebElement from wrapped object::

        >>> isinstance(br.unwrap, WebElement)
        True

* parent
    find_element_by_xpath("./parent::node()")::

        >>> price = br.by_tag("th", "Price").parent.by_tag("td").text

* performance
    Returns window.performance wrapped object::

        >>> performance = br.performance
        >>> timing = performance.timing
        >>> navigation = performance.navigation
        >>> timing.loadEventEnd
        1358319427476

* to_select
    Convert wrapped WebElement to raw Select object::

        >>> br.by_id('select_button').to_select.select_by_visible_text("hoge")

    select method returns the same as below::

        >>> br.select(id = 'select_button).select_by_visible_text("hoge")

* alert
    Returns Alert(switch_to_alert()) object::

        >>> br.alert.accept()

* current_url
    Returns current_url after loading page body::

        >>> br.current_url

* timeout
    Accessor for _timeout property.

        >>> br.timeout
        5
        >>> br.timeout = 10
        >>> br.timeout
        10

* attr(name)
    Shortcut to get_attribute::

        >>> br.attr('href')

* click(timeout=3, presleep=0, postsleep=0)
    Continue to polling until timeout or element is displayed and clickable::

        >>> br.button("Send").click()

* scroll_to(x, y)
    equivalent to javascript's scrollTo::

        >>> br.scrollTo(0, 100)

* scroll_by(x, y)
    equivalent to javascript's scrollBy::

        >>> br.scrollBy(10, 10)

* scroll_into_view(jq_identifier, align_with_top=True)
    find elements by jq_identifier and retrieve its first element and invoke scrollIntoView to it::

        >>> var element = $('#hoge');
        >>> element && element.scrollIntoView(true)

    second argument is passed as javascript's boolean to scrollIntoView::

        >>> br.scrollIntoView('#hoge', False)

* waitfor(type, target, eager=False, timeout=3)
    See source::

        >>> br.waitfor("xpath", "//input[@type='submit']")

* xpath(target, eager=False, timeout=3)
    find_element_by_xpath(target, timeout)::

        >>> buttons = br.xpath("//input[@type='submit' or @type='button']", eager=True)

* css(target, eager=False, timeout=3)
    find_element_by_css_selector(target, timeout)::

        >>> [li.text for li in br.css("ul li")]

* by_tag(self, tag, eager=False, timeout=3, \*\*attributes)
    Returns specified tagged element with specified attributes optionally.::

        >>> br.by_tag("link", rel="stylesheet")

* by_text(text, tag='*', partial=False, eager=False, timeout=3)
    similar to find_element_by_link_text or find_element_by_partial_link_text, but this method can be applicable to any tag::

        >>> br.by_text("Go back to Top Page", "a")

* by_class(target, eager=False, timeout=3)
    find_element_by_class_name(target, timeout)::

        >>> br.by_class("colored")

* by_id(target, eager=False, timeout=3)
    find_element_by_id(target, timeout)::

        >>> br.by_id("main_contents")

* by_name(target, eager=False, timeout=3)
    find_element_by_name(target, timeout)::

        >>> br.by_name("page_password")

* by_linktxt(target, eager=False, timeout=3, partial=False)
    find_element_by_link_text(target, timeout). if partial=True, then find_element_by_partial_link_text::

        >>> br.by_linktxt("Go back to", partial=True)

* href(partialurl=None, eager=False, timeout=3):
    find_element_by_xpath("//a", timeout). if partialurl was given, search 'a' tag which href contains partialurl::

        >>> phplinks = br.href(".php", eager=True)

* img(alt=None, ext=None, eager=False, timeout=3)
    find_elements_by_xpath("//img", timeout)::

        >>> br.img(alt="I am sorry", ext="sorry.gif")

* button(value, eager=False, timeout=3)
    find_element_by_xpath("//input[@type='submit' or @type='button' and @value='{}']".format(value), timeout)::

        >>> br.button("Send this form").click()

* checkbox(self, eager=False, timeout=3, \*\*attributes)
    Returns 'input' element type='checkbox'::

        >>> br.checkbox(name='checked_value', id='hoge')

* radio(self, eager=False, timeout=3, \*\*attributes)
    Retuns 'input' element type='radio'.::

        >>> br.radio(name='hoge', id='fuga').click()

* select(self, eager=False, timeout=3, \*\*attributes)
    Returns Select(self.by_tag("select", eager, timeout, \*\*attributes) or their wrapped SeleniumContainerWrapper::

        >>> br.select(name="hoge").select_by_index(1)
        >>> [select.is_multiple for select in br.select(eager=True, name="hoge")]

SeleniumContainerWrapper
^^^^^^^^^^^^^^^^^^^^^^^^

* size
    Returns length of wrapped iterable::

        >>> br.img(eager=True).size

* sample(size)
    Returns random.sample(self._iterable, size)::

        >>> br.img(eager=True).sample(10)

* choice()
    Returns random.choice(self._iterable)::

        >>> br.img(eager=True).choice()

Recent Change
-------------
* 0.4.3
    * Add **perfomance**, **performance.timing**, **performance.navigation**, **performance.memory** properties.
* 0.4.2
    * Add 'PhantomJS' support.
* 0.4.1
    * Fixed some bugs.
* 0.4.0
    * Added **scroll_to**, **scroll_by**, **scroll_into_view** methods.
* 0.3.5
    * Added **attr** method.
    * Fixed some typos.
* 0.3.4
    * Added size property to SeleniumContainerWrapper
    * Fixed to be able to change default timeout.
* 0.3.3
    * Fixed bugs of string formatting.
* 0.3.2
    * Changed **alert** to wait until Alert's text is accesible.
    * Override **current_url** to wait for page body loaded.
* 0.3.1
    * Added **connect** functon.
* 0.3.0
    * Changed **tag** method to **by_tag**.
    * Added **checkbox**, **radio**.
    * Changed **select** property to method.
    * Added **sample**, **choice** methods to SeleniumContainerWrapper.
    * Fixed **click** bug.
* 0.2.4
    * Fixed bug.
* 0.2.3
    * Added ext argument to **img** (alt and ext are both optional.)
* 0.2.2
    * Added new property **alert**
    * Changed **img**'s argument from ext to alt( find_element_by_xpath("//img[@alt='{}'.format(alt)) )
    * Modified SeleniumContainerWrapper's __contains__ behavior to unwrap given object if it is a SeleniumWrapper.
