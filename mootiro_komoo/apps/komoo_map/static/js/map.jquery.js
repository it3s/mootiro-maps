(function() {

  define(['map/maps'], function() {
    return (function($) {
      var fixMapHeight, fixMapSize, fixMapWidth, methods;
      fixMapSize = function(e) {
        var map;
        map = e.data.map;
        fixMapHeight(map);
        fixMapWidth(map);
        return map.refresh();
      };
      fixMapHeight = function(map, mapPanel) {
        var height, _ref;
        if (mapPanel == null) mapPanel = $('#map-panel');
        height = $('body').innerHeight() - $('#top').innerHeight() - $('.mootiro_bar').innerHeight() - 5;
        $(map.element).height(height);
        mapPanel.height(height);
        return $('.panel', mapPanel).height(height - ((_ref = window.community_slug) != null ? _ref : {
          170: 146
        }));
      };
      fixMapWidth = function(map, mapPanel) {
        var panelLeft, panelWidth;
        if (mapPanel == null) mapPanel = $('#map-panel');
        panelWidth = mapPanel.innerWidth();
        try {
          panelLeft = mapPanel.position().left;
        } catch (err) {
          panelLeft = 0;
        }
        return $(map.element).css({
          marginLeft: panelWidth + panelLeft,
          width: 'auto'
        });
      };
      methods = {
        init: function(options) {
          return this.each(function() {
            var $this, map, opts;
            $this = $(this);
            $this.addClass('komoo-map-googlemap');
            opts = $.extend({
              element: $this.get(0)
            }, $.fn.komooMap.defaults, options);
            if (opts.width != null) $this.width(opts.width);
            if (opts.height != null) $this.height(opts.height);
            map = komoo.maps.makeMap(opts);
            $this.data('map', map);
            if (opts.mapType != null) map.googleMap.setMapTypeId(opts.mapType);
            if (opts.height === '100%') {
              $(window).resize({
                map: map
              }, fixMapSize);
              return $(window).resize();
            }
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
        },
        highlight: function(opts) {
          $(this).data('map').highlightFeature(opts.type, opts.id);
          return $(this);
        },
        resize: function() {
          return $(window).resize();
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
