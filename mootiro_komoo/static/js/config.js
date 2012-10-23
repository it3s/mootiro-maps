(function() {
  var baseUrl, config;

  baseUrl = (typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.require_baseUrl : void 0) || '/static/js';

  config = {
    baseUrl: baseUrl,
    paths: {
      'lib': '../lib',
      'text': '../lib/requirejs/text',
      'templates': '../templates',
      'ad-gallery': '../ad_gallery/jquery.ad-gallery.min',
      'ajaxforms': '../js/ajaxforms',
      'jquery': '../lib/jquery-1.7.1.min',
      'jquery-ui': '../lib/jquery-ui-1.8.16/jquery-ui-1.8.16.min',
      'bootstrap': '../lib/bootstrap.min',
      'underscore': '../lib/underscore-min',
      'backbone': '../lib/backbone-min',
      'async': '../lib/requirejs/async',
      'goog': '../lib/requirejs/goog',
      'propertyParser': '../lib/requirejs/propertyParser',
      'infobox': 'vendor/infobox_packed',
      'markerclusterer': 'vendor/markerclusterer_packed',
      'canvasloader': '../lib/heartcode-canvasloader-min',
      'sinon': '../lib/sinon-1.5.0'
    },
    shim: {
      'utils': {
        deps: ['jquery']
      },
      'ajaxforms': {
        deps: ['jquery']
      },
      'jquery-ui': {
        deps: ['jquery']
      },
      'bootstrap': {
        deps: ['jquery']
      },
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
      },
      'canvasloader': {
        exports: 'CanvasLoader'
      },
      'sinon': {
        exports: 'sinon'
      }
    },
    deps: ['map/compat', 'map/utils']
  };

  if (typeof requirejs !== "undefined" && requirejs !== null) {
    requirejs.config(config);
  }

  if (window.require == null) window.require = config;

}).call(this);
