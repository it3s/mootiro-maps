(function() {

  define(['common'], function() {
    require(['analytics', 'facebook-jssdk'], function(analytics, facebook) {
      analytics.init();
      return facebook.init(typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.facebookAppId : void 0);
    });
    require(['moderation/moderation', 'lib/shortcut', 'ajaxforms', 'komoo_search', 'utils', 'no-ie'], function() {});
    return {};
  });

}).call(this);
