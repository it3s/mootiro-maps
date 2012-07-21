(function() {
  var AjaxBalloon, Balloon, FeatureClusterer, InfoWindow, Tooltip, _base,
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

    Balloon.prototype.createInfoBox = function(options) {
      return this.setInfoBox(new InfoBox({
        pixelOffset: new google.maps.Size(0, -20),
        enableEventPropagation: true,
        closeBoxMargin: "10px",
        disableAutoPan: true,
        boxStyle: {
          cursor: "pointer",
          background: "url(/static/img/infowindow-arrow.png) no-repeat 0 10px",
          width: this.width
        }
      }));
    };

    Balloon.prototype.setInfoBox = function(infoBox) {
      this.infoBox = infoBox;
    };

    Balloon.prototype.setMap = function(map) {
      this.map = map;
    };

    Balloon.prototype.open = function(options) {
      var newPosition, point, position, _ref, _ref2;
      this.options = options != null ? options : {};
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
      var _ref;
      this.isMouseover = false;
      this.infoBox.close();
      if ((_ref = this.feature) != null ? _ref.isHighlighted() : void 0) {
        this.feature.setHighlight(false);
      }
      return this.feature = null;
    };

    Balloon.prototype.customize = function() {
      var _this = this;
      google.maps.event.addDomListener(this.infoBox, "domread", function(e) {
        var div;
        div = _this.infoBox.div_;
        google.maps.event.addDomListener(div, "click", function(e) {
          e.cancelBubble = true;
          return typeof e.stopPropagation === "function" ? e.stopPropagation() : void 0;
        });
        google.maps.event.addDomListener(div, "mouseout", function(e) {
          return _this.isMouseover = false;
        });
        return komoo.event.trigger(_this, "domready");
      });
      return this.initDomElements();
    };

    Balloon.prototype.initDomElements = function() {
      var _this = this;
      this.title = $("<div>");
      this.body = $("<div>");
      this.content = $("<div>").addClass("map-infowindow-content");
      this.content.append(this.title);
      this.content.append(this.body);
      this.content.css({
        background: "white",
        padding: "10px",
        margin: "0 0 0 15px"
      });
      this.content.hover(function(e) {
        return _this.isMouseover = true;
      }, function(e) {
        return _this.isMouseover = false;
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
      body = "<ul>" + (body.join('')) + "</ul>";
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
      var feature, url,
        _this = this;
      if (options == null) options = {};
      feature = options.feature;
      if (!feature) return;
      if (feature[this.contentViewName]) return feature[this.contentViewName];
      url = dutils.urls.resolve(this.contentViewName, {
        zoom: this.map.getZoom(),
        app_label: feature.featureType.appLabel,
        model_name: feature.featureType.modelName,
        obj_id: feature.getProperty("id")
      });
      $.get(url, function(data) {
        feature[_this.contentViewName] = data;
        return _this.setContent(data);
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
      var _this = this;
      InfoWindow.__super__.customize.call(this);
      return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
        var closeBox, div;
        div = _this.infoBox.div_;
        google.maps.event.addDomListener(div, "mouseover", function(e) {
          _this.isMouseover = e.offsetX > 10 || e.toElement !== div;
          if (_this.isMouseover) {
            e.cancelBubble = true;
            if (typeof e.preventDefault === "function") e.preventDefault();
            if (typeof e.stopPropagation === "function") e.stopPropagation();
            return _this.map.closeTooltip();
          }
        });
        closeBox = div.firstChild;
        google.maps.event.addDomListener(closeBox, "click", function(e) {
          return _this.close();
        });
        return google.maps.event.addDomListener(closeBox, "mouseover", function(e) {
          return _this.isMouseover = true;
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
      var _this = this;
      Tooltip.__super__.customize.call(this);
      return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
        var closeBox, div;
        div = _this.infoBox.div_;
        google.maps.event.addDomListener(div, "click", function(e) {
          return _this.map.openInfoWindow(_this.options);
        });
        closeBox = div.firstChild;
        return $(closeBox).hide();
      });
    };

    return Tooltip;

  })(AjaxBalloon);

  FeatureClusterer = (function() {

    FeatureClusterer.prototype.maxZoom = 9;

    FeatureClusterer.prototype.gridSize = 20;

    FeatureClusterer.prototype.minSize = 1;

    FeatureClusterer.prototype.imagePath = '/static/img/cluster/communities';

    FeatureClusterer.prototype.imageSizes = [24, 29, 35, 41, 47];

    function FeatureClusterer(options) {
      var _base2, _base3, _base4, _base5, _base6;
      this.options = options != null ? options : {};
      if ((_base2 = this.options).gridSize == null) {
        _base2.gridSize = this.gridSize;
      }
      if ((_base3 = this.options).maxZoom == null) _base3.maxZoom = this.maxZoom;
      if ((_base4 = this.options).minimumClusterSize == null) {
        _base4.minimumClusterSize = this.minSize;
      }
      if ((_base5 = this.options).imagePath == null) {
        _base5.imagePath = this.imagePath;
      }
      if ((_base6 = this.options).imageSizes == null) {
        _base6.imageSizes = this.imageSizes;
      }
      this.setMap(this.options.map);
      this.features = [];
      this.initMarkerClusterer(this.options);
      this.initEvents();
    }

    FeatureClusterer.prototype.initMarkerClusterer = function(options) {
      var map, _ref;
      if (options == null) options = {};
      map = ((_ref = this.map) != null ? _ref.googleMap : void 0) || this.map;
      return this.clusterer = new MarkerClusterer(map, [], options);
    };

    FeatureClusterer.prototype.initEvents = function(object) {
      var eventsNames,
        _this = this;
      if (object == null) object = this.clusterer;
      if (!object) return;
      eventsNames = ['clusteringbegin', 'clusteringend'];
      eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(object, eventName, function(mc) {
          return komoo.event.trigger(_this, eventName, _this);
        });
      });
      eventsNames = ['click', 'mouseout', 'mouseover'];
      return eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(object, eventName, function(c) {
          var features, marker;
          features = komoo.collections.makeFeatureCollection({
            features: (function() {
              var _i, _len, _ref, _results;
              _ref = c.getMarkers();
              _results = [];
              for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                marker = _ref[_i];
                _results.push(marker.feature);
              }
              return _results;
            })()
          });
          return komoo.event.trigger(_this, eventName, features, c.getCenter());
        });
      });
    };

    FeatureClusterer.prototype.setMap = function(map) {
      this.map = map;
    };

    FeatureClusterer.prototype.updateLength = function() {
      return this.length = this.features.length;
    };

    FeatureClusterer.prototype.clear = function() {
      this.features = [];
      this.clusterer.clearMarkers();
      return this.updateLength();
    };

    FeatureClusterer.prototype.getAt = function(index) {
      return this.features[index];
    };

    FeatureClusterer.prototype.push = function(element) {
      if (element.getMarker()) {
        this.features.push(element);
        element.getMarker().setVisible(false);
        this.clusterer.addMarker(element.getMarker().getOverlay());
        return this.updateLength();
      }
    };

    FeatureClusterer.prototype.pop = function() {
      var element;
      element = this.features.pop();
      this.clusterer.removeMarker(element.getMarker());
      this.updateLength();
      return element;
    };

    FeatureClusterer.prototype.forEach = function(callback, thisArg) {
      return this.features.forEach(callback, thisArg);
    };

    FeatureClusterer.prototype.repaint = function() {
      return this.clusterer.repaint();
    };

    FeatureClusterer.prototype.getAverageCenter = function() {
      return this.clusterer.getAverageCenter();
    };

    FeatureClusterer.prototype.addFeatures = function(features) {
      var _this = this;
      return features != null ? features.forEach(function(feature) {
        return _this.push(feature);
      }) : void 0;
    };

    return FeatureClusterer;

  })();

  window.komoo.controls = {
    Balloon: Balloon,
    AjaxBalloon: AjaxBalloon,
    InfoWindow: InfoWindow,
    Tooltip: Tooltip,
    FeatureClusterer: FeatureClusterer,
    makeInfoWindow: function(options) {
      return new InfoWindow(options);
    },
    makeTooltip: function(options) {
      return new Tooltip(options);
    },
    makeFeatureClusterer: function(options) {
      return new FeatureClusterer(options);
    }
  };

}).call(this);
