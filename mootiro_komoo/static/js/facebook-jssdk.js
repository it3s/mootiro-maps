define(['jquery'], function ($) {
    return {
        init: function (appId) {
            // Creates the fb-root element
            var fbRoot = $('<div id="fb-root" />');
            $('body').prepend(fbRoot);

            // Code from Facebook documentation
            (function(d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) return;
                js = d.createElement(s); js.id = id;
                js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=" + appId;
                fjs.parentNode.insertBefore(js, fjs);
            }(document, 'script', 'facebook-jssdk'));
        }
    }
});
