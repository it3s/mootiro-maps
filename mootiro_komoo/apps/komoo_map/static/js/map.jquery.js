(function() {

  define(['map/maps'], function() {
    return (function($) {
      var methods;
      methods = {
        init: function(options) {
          return this.each(function() {
            var $this, opts;
            $this = $(this);
            opts = $.extend({
              element: $this.get(0)
            }, $.fn.komooMap.defaults, options);
            return $this.data('map', komoo.maps.makeMap(opts));
          });
        },
        edit: function(feature) {
          $(this).data('map').editFeature(feature);
          return $(this);
        },
        geojson: function(geojson) {
          if (!(geojson != null)) {
            return $(this).data('map').getGeoJson();
          } else {
            return $(this).data('map').loadGeoJson(geojson);
          }
        },
        goTo: function(opts) {
          var _ref;
          $(this).data('map').goTo((_ref = opts.position) != null ? _ref : opts.address, opts.displayMarker);
          return $(this);
        }
      };
      $.fn.komooMap = function(method) {
        if (methods[method]) {
          return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
          return methods.init.apply(this, arguments);
        } else {
          return $.error("Method " + method + " does not exist on jQuery.komooMap");
        }
      };
      return $.fn.komooMap.defaults = {
        type: 'editor'
      };
    })(jQuery);
  });

}).call(this);
