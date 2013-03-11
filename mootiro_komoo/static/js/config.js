(function() {
  var baseUrl, config, _ref;

  baseUrl = ((_ref = window.komooNS) != null ? _ref.require_baseUrl : void 0) || '/static/js';

  config = {
    baseUrl: baseUrl,
    paths: {
      'lib': '../lib',
      'templates': '../templates',
      'spock-gallery': '../spock_gallery/jquery.spock-gallery.min',
      'jquery': '../lib/jquery-1.7.1.min',
      'underscore': '../lib/underscore-min',
      'backbone': '../lib/backbone-min',
      'async': '../lib/requirejs/async',
      'goog': '../lib/requirejs/goog',
      'text': '../lib/requirejs/text',
      'propertyParser': '../lib/requirejs/propertyParser',
      'infobox': 'vendor/infobox_packed',
      'markerclusterer': 'vendor/markerclusterer_packed'
    },
    shim: {
      'underscore': {
        exports: '_'
      },
      'backbone': {
        deps: ['underscore', 'jquery'],
        exports: 'Backbone'
      },
      'infobox': {
        deps: ['googlemaps'],
        exports: 'InfoBox'
      },
      'markerclusterer': {
        deps: ['googlemaps'],
        exports: 'MarkerClusterer'
      }
    },
    deps: ['map/compat', 'map/utils']
  };

  if (typeof requirejs !== "undefined" && requirejs !== null) {
    requirejs.config(config);
  }

  if (window.require == null) window.require = config;

}).call(this);
