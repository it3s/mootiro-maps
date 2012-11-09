(function() {

  define(['jquery', 'map_filter', 'utils'], function($) {
    var Panel;
    Panel = (function() {

      function Panel(map) {
        var onHashChange;
        this.tabs = new Tabs('.panel-tab', '.panel');
        onHashChange = function() {
          var hash;
          hash = window.location.hash;
          return $(hash + '-tab').click();
        };
        onHashChange();
        window.onhashchange = onHashChange;
        this.menu = $("#map-add-menu");
        this.connect(map);
      }

      Panel.prototype.onDrawingStarted = function(feature) {
        var menuItem;
        this.menu.find('.item').removeClass('selected');
        this.menu.find('.sublist').hide();
        this.menu.find('.collapser i.icon-chevron-down').toggleClass('icon-chevron-right icon-chevron-down');
        menuItem = this.menu.find('.' + feature.getType().toLowerCase() + ' .item');
        menuItem.addClass('selected');
        return this.menu.addClass('frozen');
      };

      Panel.prototype.onDrawingFinished = function(feature) {
        this.menu.find('.item').removeClass('selected');
        return this.menu.removeClass('frozen');
      };

      Panel.prototype.connect = function(map) {
        var that;
        if (typeof console !== "undefined" && console !== null) {
          console.log('Connecting panel');
        }
        that = this;
        this.menu.find('.item, .sublist li > div').click(function(e) {
          var item;
          if (that.menu.hasClass('frozen')) return false;
          item = $(this);
          if (item.attr('data-geometry-type')) {
            return map.drawNewFeature(item.attr('data-geometry-type'), item.attr('data-feature-type'));
          } else {
            return $('.collapser', item.parent()).click();
          }
        });
        $('#collapse-panel').click(function(ev) {
          var $parent, interval;
          $parent = $("#main-map-panel").parent();
          $parent.toggleClass("collapsed");
          if (map != null) map.refresh();
          interval = setInterval((function() {
            return map != null ? map.refresh() : void 0;
          }), 500);
          return setTimeout((function() {
            return clearInterval(interval);
          }), 1000);
        });
        map.subscribe('drawing_started', this.onDrawingStarte, this);
        map.subscribe('drawing_finished', this.onDrawingFinished, this);
        $('#map-panel').show();
        return $(window).resize();
      };

      return Panel;

    })();
    return Panel;
  });

}).call(this);
