(function() {
  var config;

  config = {
    baseUrl: '/static/js',
    paths: {
      'lib': '../lib',
      'ad-gallery': '../ad_gallery/jquery.ad-gallery.min',
      'jquery': '../lib/jquery-1.7.1.min',
      'underscore': '../lib/underscore-min',
      'backbone': '../lib/backbone-min'
    },
    shim: {
      'underscore': {
        exports: '_'
      },
      'backbone': {
        deps: ['underscore', 'jquery'],
        exports: 'Backbone'
      }
    },
    deps: ['map/compat', 'map/utils']
  };

  if (typeof requirejs !== "undefined" && requirejs !== null) {
    requirejs.config(config);
  }

  if (window.require == null) window.require = config;

}).call(this);
