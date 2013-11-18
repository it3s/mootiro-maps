var baseUrl, config, _ref, require;

baseUrl = ((_ref = window.KomooNS) != null ? _ref.require_baseUrl : void 0) || '/static/js';

config = {
  baseUrl: baseUrl,
  waitSeconds: 0,
  paths: {
    'lib': '../lib',
    'templates': '../templates',
    'spock-gallery': '../spock_gallery/jquery.spock-gallery.min',
    'async': '../lib/requirejs/async',
    'goog': '../lib/requirejs/goog',
    'text': '../lib/requirejs/text',
    'propertyParser': '../lib/requirejs/propertyParser',
    'infobox': 'vendor/infobox_packed',
    'reForm': '../lib/reForm',
    'markerclusterer': 'vendor/markerclusterer_packed'
  },
  shim: {
    'infobox': {
      deps: ['googlemaps'],
      exports: 'InfoBox'
    },
    'reForm': {
      deps: ['jquery', 'underscore', 'backbone'],
      exports: 'reForm'
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

if (require == null) require = config;

