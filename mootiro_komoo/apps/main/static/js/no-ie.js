(function() {
  var message, template, theOneWhoShallNotBeNamed;

  theOneWhoShallNotBeNamed = 'Microsoft Internet Explorer';

  message = "We detected you are using Internet Explorer. We don't have support for this browser yet. We ask sorry, but we are working on it.\n<br/>\nConsider using <strong>Mozilla Firefox</strong>. He is faster, more secure and more stable. And it is <strong>free</strong>.\nGo to the following page, download Firefox and enjoy a better web experience: <a href=\"http://www.mozilla.org/\" >http://www.mozilla.org/</a><br/>\nThe reason for this is: IE is slow, very insecure, and don't follow the web standards, so adding support for it is quite problematic and time consuming.\nIf you cannot, anyhow, install another browser, you may have several issues. Thanks for your comprehension.";

  template = "<div id=\"ie-warning\">\n  <img src=\"/static/img/erro.png\" />\n  " + message + "\n</div>";

  $(function() {
    if (navigator.appName === theOneWhoShallNotBeNamed) {
      return $('#top').append(gettext(template));
    }
  });

}).call(this);
