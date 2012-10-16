theOneWhoShallNotBeNamed = 'Microsoft Internet Explorer'
# theOneWhoShallNotBeNamed = "Netscape"  # this is for testing

message = """
  We detected you are using Internet Explorer. We don't have support for this browser yet. We ask sorry, but we are working on it.
  <br/>
  Consider using <strong>Mozilla Firefox</strong>. He is faster, more secure and more stable. And it is <strong>free</strong>.
  Go to the following page, download Firefox and enjoy a better web experience: <a href="http://www.mozilla.org/" >http://www.mozilla.org/</a><br/>
  The reason for this is: IE is slow, very insecure, and don't follow the web standards, so adding support for it is quite problematic and time consuming.
  If you cannot, anyhow, install another browser, you may have several issues. Thanks for your comprehension.
"""

template = """
<div id="ie-warning">
  <img src="/static/img/erro.png" />
  #{message}
</div>
"""

$ ->
  if navigator.appName is theOneWhoShallNotBeNamed
    $('#top').append gettext template
