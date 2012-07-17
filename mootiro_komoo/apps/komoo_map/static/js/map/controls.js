(function() {
  var AjaxBalloon, Balloon, InfoWindow, Tooltip, _base,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

  Balloon = (function() {

    Balloon.prototype.defaultWidth = "300px";

    function Balloon(options) {
      this.options = options != null ? options : {};
      this.width = options.width || this.defaultWidth;
      this.createInfoBox(this.options);
      this.setMap(this.options.map);
      this.customize();
    }

    createInfoBox(function(options) {
      return this.setInfoBox(new InfoBox({
        pixelOffset: new google.maps.Size(0)
      }, -20, {
        enableEventPropagation: true,
        closeBoxMargin: "10px",
        disableAutoPan: true,
        boxStyle: {
          cursor: "pointer",
          background: "url(/static/img/infowindow-arrow.png) no-repeat 0 10px",
          width: this.width
        }
      }));
    });

    Balloon.prototype.setInfoBox = function(infoBox) {
      this.infoBox = infoBox;
    };

    Balloon.prototype.setMap = function(setMap) {
      this.setMap = setMap;
    };

    Balloon.prototype.open = function(options) {
      var newPosition, point, position, _ref, _ref2;
      if (options == null) options = {};
      if (((_ref = this.map) != null ? _ref.mode : void 0) !== komoo.Mode.NAVIGATE) {
        return;
      }
      this.setContent(options.content || (options.features ? this.createClusterContent(options) : this.createFeatureContent(options)));
      this.feature = options.feature || ((_ref2 = options.features) != null ? _ref2[0] : void 0);
      position = options.position || this.feature.getCenter();
      point = komoo.utils.latLngToPoint(this.map, position);
      point.x += 5;
      newPosition = komoo.utils.pointToLatLng(this.map, point);
      this.infoBox.setPosition(newPosition);
      return this.infoBox.open(this.map.googleMap || this.map);
    };

    Balloon.prototype.setContent = function(content) {
      if (content == null) {
        content = {
          title: "",
          body: ""
        };
      }
      if (typeof content === "string") {
        content = {
          title: "",
          url: "",
          body: content
        };
      }
      this.title.html(content.url ? "<a href=\"" + content.url + "\">" + content.title + "</a>" : content.title);
      return this.body.html(content.body);
    };

    Balloon.prototype.close = function() {
      this.infoBox.close();
      if (this.feature.isHighlighted) this.feature.setHighlight(false);
      this.feature = null;
      return this.isMouseover = false;
    };

    Balloon.prototype.customize = function() {
      var that;
      that = this;
      google.maps.event.addDomListener(this.infoBox, "domread", function(e) {
        var closeBox, div;
        div = that.infoBox.div_;
        google.maps.event.addDomListener(div, "click", function(e) {
          e.cancelBubble = true;
          return typeof e.stopPropagation === "function" ? e.stopPropagation() : void 0;
        });
        google.maps.event.addDomListener(div, "mouseout", function(e) {
          return that.isMouseover = false;
        });
        closeBox = div.firstChild;
        google.maps.event.addDomListener(closeBox, "click", function(e) {
          return that.close();
        });
        google.maps.event.addDomListener(closeBox, "mouseover", function(e) {
          return that.isMouseover = true;
        });
        return komoo.event.trigger(that, "domready");
      });
      return this.initDomElements();
    };

    Balloon.prototype.initDomElements = function() {
      var that;
      that = this;
      this.title = $("<div>");
      this.body = $("<div>");
      this.content = $("<div>").addClass("map-infowindow-content");
      this.content.append(this.title);
      this.content.append(this.body);
      this.content.css({
        background: "white"
      });
      ({
        padding: "10px",
        margin: "0 0 0 15px"
      });
      this.content.hover(function(e) {
        return that.isMouseover = true;
      }, function(e) {
        return that.isMouseover = false;
      });
      return this.infoBox.setContent(this.content.get(0));
    };

    Balloon.prototype.createClusterContent = function(options) {
      var body, feature, features, msg, title;
      if (options == null) options = {};
      features = options.features || [];
      msg = ngettext("%s Community", "%s Communities", features.length);
      title = "<strong>" + (interpolate(msg, [features.length])) + "</strong>";
      body = (function() {
        var _i, _len, _ref, _results;
        _ref = features.slice(0, 11);
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          feature = _ref[_i];
          _results.push("<li>" + (feature.getProperty('name')) + "</li>");
        }
        return _results;
      })();
      body = "<ul>" + (body.join()) + "</ul>";
      return {
        title: title,
        url: "",
        body: body
      };
    };

    Balloon.prototype.createFeatureContent = function(options) {
      var feature, title;
      if (options == null) options = {};
      title = "";
      feature = options.feature;
      if (feature) {
        title = feature.getProperty("type") === "OrganizationBranch" ? feature.getProperty("organization_name") + " - " + feature.getProperty("name") : feature.getProperty("name");
      }
      return {
        title: title,
        url: "",
        body: ""
      };
    };

    return Balloon;

  })();

  AjaxBalloon = (function(_super) {

    __extends(AjaxBalloon, _super);

    function AjaxBalloon() {
      AjaxBalloon.__super__.constructor.apply(this, arguments);
    }

    AjaxBalloon.prototype.createFeatureContent = function(options) {
      var feature, that, url;
      if (options == null) options = {};
      that = this;
      feature = options.feature || {};
      if (!feature) return;
      if (feature[this.contentViewName]) return feature[this.contentViewName];
      url = dutils.urls.resolve(this.contentViewName, {
        zoom: this.map.getZoom(),
        app_label: feature.featureType.appLabel,
        model_name: feature.featureType.modelName,
        obj_id: feature.getProperty("id")
      });
      $.get(url, function(data) {
        feature[that.contentViewName] = data;
        return that.setContent(data);
      });
      return gettext("Loading...");
    };

    return AjaxBalloon;

  })(Balloon);

  InfoWindow = (function(_super) {

    __extends(InfoWindow, _super);

    function InfoWindow() {
      InfoWindow.__super__.constructor.apply(this, arguments);
    }

    InfoWindow.prototype.defaultWidth = "350px";

    InfoWindow.prototype.contentViewName = "info_window";

    InfoWindow.prototype.customize = function() {
      var that;
      InfoWindow.__super__.customize.call(this);
      that = this;
      return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
        var div;
        div = that.infoBox.div_;
        return google.maps.event.addDomListener(div, "mousemove", function(e) {
          that.isMouseover = e.offsetX > 10 || e.toElement !== div;
          if (that.isMouseover) {
            e.cancelBubble = true;
            if (typeof e.preventDefault === "function") e.preventDefault();
            if (typeof e.stopPropagation === "function") e.stopPropagation();
            return that.map.closeTooltip();
          }
        });
      });
    };

    return InfoWindow;

  })(AjaxBalloon);

  Tooltip = (function(_super) {

    __extends(Tooltip, _super);

    function Tooltip() {
      Tooltip.__super__.constructor.apply(this, arguments);
    }

    Tooltip.prototype.contentViewName = "tooltip";

    Tooltip.prototype.customize = function() {
      var that;
      Tooltip.__super__.customize.call(this);
      that = this;
      return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
        var closeBox, div;
        div = that.infoBox.div_;
        google.maps.event.addDomListener(div("click", function(e) {
          return that.map.openInfoWindow(that.options);
        }));
        closeBox = div.firstChild;
        return $(closeBox).hide();
      });
    };

    return Tooltip;

  })(AjaxBalloon);

  window.komoo.controls = {
    Balloon: Balloon,
    AjaxBalloon: AjaxBalloon,
    InfoWindow: InfoWindow,
    Tooltip: Tooltip,
    makeInfoWindow: function(options) {
      return new InfoWindow(options);
    },
    makeTooltip: function(options) {
      return new Tooltip(options);
    }
  };

}).call(this);
