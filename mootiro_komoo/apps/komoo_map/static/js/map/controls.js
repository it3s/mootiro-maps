(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(['map/geometries', 'vendor/infobox_packed', 'vendor/markerclusterer_packed'], function() {
    var ADD, AjaxBalloon, AutosaveLocation, Balloon, Box, CUTOUT, DELETE, DrawingControl, DrawingManager, EDIT, FeatureClusterer, InfoWindow, LicenseBox, Location, NEW, OVERLAY, PERIMETER_SELECTION, PerimeterSelector, SaveLocation, StreetView, SupporterBox, Tooltip, _base;
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = google.maps.event;
    OVERLAY = {};
    OVERLAY[komoo.geometries.types.POINT] = google.maps.drawing.OverlayType.MARKER;
    OVERLAY[komoo.geometries.types.MULTIPOINT] = google.maps.drawing.OverlayType.MARKER;
    OVERLAY[komoo.geometries.types.LINESTRING] = google.maps.drawing.OverlayType.POLYLINE;
    OVERLAY[komoo.geometries.types.MULTILINESTRING] = google.maps.drawing.OverlayType.POLYLINE;
    OVERLAY[komoo.geometries.types.POLYGON] = google.maps.drawing.OverlayType.POLYGON;
    EDIT = 'edit';
    DELETE = 'delete';
    NEW = 'new';
    ADD = 'add';
    CUTOUT = 'cutout';
    PERIMETER_SELECTION = 'perimeter_selection';
    Box = (function() {

      Box.prototype.position = google.maps.ControlPosition.RIGHT_BOTTOM;

      function Box() {
        this.box = $("<div>");
        if (this.id != null) this.box.attr("id", this.id);
        if (this["class"] != null) this.box.addClass(this["class"]);
      }

      Box.prototype.setMap = function(map) {
        this.map = map;
        this.map.googleMap.controls[this.position].push(this.box.get(0));
        return typeof this.handleMapEvents === "function" ? this.handleMapEvents() : void 0;
      };

      return Box;

    })();
    SupporterBox = (function(_super) {

      __extends(SupporterBox, _super);

      SupporterBox.prototype.id = "map-supporters";

      function SupporterBox() {
        SupporterBox.__super__.constructor.call(this);
        this.box.append($("#map-supporters-content").show());
      }

      return SupporterBox;

    })(Box);
    LicenseBox = (function(_super) {

      __extends(LicenseBox, _super);

      LicenseBox.prototype.id = "map-license";

      LicenseBox.prototype.position = google.maps.ControlPosition.BOTTOM_LEFT;

      function LicenseBox() {
        LicenseBox.__super__.constructor.call(this);
        this.box.html('Este conteúdo é disponibilizado nos termos da licença <a href="http://creativecommons.org/licenses/by-sa/3.0/deed.pt_BR">Creative Commons - Atribuição - Partilha nos Mesmos Termos 3.0 Não Adaptada</a>; pode estar sujeito a condições adicionais. Para mais detalhes, consulte as Condições de Uso.');
      }

      return LicenseBox;

    })(Box);
    DrawingManager = (function() {

      DrawingManager.prototype.enabled = true;

      DrawingManager.prototype.defaultDrawingManagerOptions = {
        drawingControl: false,
        drawingMode: null
      };

      DrawingManager.prototype.componentOriginalStatus = {};

      function DrawingManager(options) {
        var _base2;
        this.options = options != null ? options : {};
        if ((_base2 = this.options).drawingManagerOptions == null) {
          _base2.drawingManagerOptions = this.defaultDrawingManagerOptions;
        }
        if (this.options.map) this.setMap(this.options.map);
      }

      DrawingManager.prototype.initManager = function(options) {
        if (options == null) options = this.defaultDrawingManagerOptions;
        this.manager = new google.maps.drawing.DrawingManager(options);
        return this.handleManagerEvents();
      };

      DrawingManager.prototype.setMap = function(map) {
        this.map = map;
        this.options.drawingManagerOptions.map = this.map.googleMap;
        this.initManager(this.options.drawingManagerOptions);
        return this.handleMapEvents();
      };

      DrawingManager.prototype.enable = function() {
        return this.enabled = true;
      };

      DrawingManager.prototype.disable = function() {
        return this.enabled = false;
      };

      DrawingManager.prototype.setMode = function(mode) {
        var _ref;
        this.mode = mode;
        this.manager.setDrawingMode(((_ref = this.mode) === ADD || _ref === NEW) || (this.mode === CUTOUT && this.feature.getGeometryType() === komoo.geometries.types.POLYGON) ? OVERLAY[this.feature.getGeometryType()] : null);
        if (this.mode === CUTOUT && this.feature.getGeometryType() !== komoo.geometries.types.POLYGON) {
          return this.mode = EDIT;
        }
      };

      DrawingManager.prototype.handleMapEvents = function() {
        var _this = this;
        komoo.event.addListener(this.map, 'draw_feature', function(geometryType, feature) {
          return _this.drawFeature(feature);
        });
        komoo.event.addListener(this.map, 'edit_feature', function(feature) {
          return _this.editFeature(feature);
        });
        komoo.event.addListener(this.map, 'drawing_finished', function(feature) {
          _this.feature.setEditable(false);
          _this.feature.updateIcon();
          _this.setFeature(null);
          return _this.setMode(null);
        });
        komoo.event.addListener(this.map, 'finish_drawing', function() {
          return komoo.event.trigger(_this.map, 'drawing_finished', _this.feature, true);
        });
        komoo.event.addListener(this.map, 'cancel_drawing', function() {
          return komoo.event.trigger(_this.map, 'drawing_finished', _this.feature, false);
        });
        komoo.event.addListener(this.map, 'mode_changed', function(mode) {
          return _this.setMode(mode);
        });
        return komoo.event.addListener(this.map, 'feature_rightclick', function(e, feature) {
          var overlay, path, paths;
          if (!(e.vertex != null)) return;
          overlay = feature.getGeometry().getOverlay();
          paths = typeof overlay.getPaths === "function" ? overlay.getPaths() : void 0;
          path = paths != null ? paths.getAt(e.path) : void 0;
          if (path != null) path.removeAt(e.vertex);
          if ((path != null ? path.getLength() : void 0) === 1) {
            return paths.removeAt(e.path);
          }
        });
      };

      DrawingManager.prototype.handleManagerEvents = function() {
        var _this = this;
        return komoo.event.addListener(this.manager, 'overlaycomplete', function(e) {
          var orientation, orientationAdded, path, paths, sArea, sAreaAdded, _ref, _ref2, _ref3, _ref4, _ref5, _ref6, _ref7;
          path = (_ref = e.overlay) != null ? typeof _ref.getPath === "function" ? _ref.getPath() : void 0 : void 0;
          if (path && ((_ref2 = _this.mode) === ADD || _ref2 === NEW || _ref2 === CUTOUT) && ((_ref3 = e.overlay) != null ? _ref3.getPaths : void 0)) {
            paths = _this.feature.getGeometry().getPaths();
            if (_this.mode === NEW) paths.clear();
            if ((paths != null ? paths.length : void 0) > 0) {
              sArea = google.maps.geometry.spherical.computeSignedArea(path);
              sAreaAdded = google.maps.geometry.spherical.computeSignedArea(paths.getAt(0));
              orientation = sArea / Math.abs(sArea);
              orientationAdded = sAreaAdded / Math.abs(sAreaAdded);
              if ((orientation === orientationAdded && _this.mode === CUTOUT) || (orientation !== orientationAdded && ((_ref4 = _this.mode) === ADD || _ref4 === NEW))) {
                path = new google.maps.MVCArray(path.getArray().reverse());
              }
            }
            paths.push(path);
            _this.feature.getGeometry().setPaths(paths);
            e.overlay.setMap(null);
          } else if (((_ref5 = _this.mode) === ADD || _ref5 === NEW) && e.overlay.getPosition) {
            _this.feature.getGeometry().addMarker(e.overlay);
            _this.feature.updateIcon(100);
          } else if (((_ref6 = _this.mode) === ADD || _ref6 === NEW) && e.overlay.getPath) {
            _this.feature.getGeometry().addPolyline(e.overlay, true);
          }
          _this.map.setMode(EDIT);
          return (_ref7 = _this.feature) != null ? _ref7.setEditable(true) : void 0;
        });
      };

      DrawingManager.prototype.setFeature = function(feature) {
        var _this = this;
        this.feature = feature;
        if (this.featureClickListener != null) {
          komoo.event.removeListener(this.featureClickListener);
        }
        if (!(this.feature != null)) return;
        this.feature.setMap(this.map, {
          geometry: true
        });
        return this.featureClickListener = komoo.event.addListener(this.feature, 'click', function(e, o) {
          var index, marker, markers, paths, polyline, polylines;
          if (_this.mode === DELETE) {
            if (_this.feature.getGeometryType() === komoo.geometries.types.POLYGON) {
              paths = _this.feature.getGeometry().getPaths();
              paths.forEach(function(path, index) {
                if (komoo.utils.isPointInside(e.latLng, path)) {
                  return paths.removeAt(index);
                }
              });
            } else if (o && _this.feature.getGeometryType() === komoo.geometries.types.MULTIPOINT) {
              markers = _this.feature.getGeometry().getMarkers();
              index = $.inArray(o, markers.getArray());
              if (index > -1) {
                marker = markers.removeAt(index);
                marker.setMap(null);
              }
            } else if (o && _this.feature.getGeometryType() === komoo.geometries.types.MULTILINESTRING) {
              polylines = _this.feature.getGeometry().getPolylines();
              index = $.inArray(o, polylines.getArray());
              if (index > -1) {
                polyline = polylines.removeAt(index);
                polyline.setMap(null);
              }
            }
            return _this.map.setMode(EDIT);
          }
        });
      };

      DrawingManager.prototype.editFeature = function(feature) {
        var options;
        if (this.enabled === false) return;
        this.setFeature(feature);
        this.feature.setEditable(true);
        options = {};
        options["" + OVERLAY[this.feature.getGeometryType()] + "Options"] = this.feature.getGeometry().getOverlayOptions({
          strokeWeight: 2.5,
          zoom: 100
        });
        this.manager.setOptions(options);
        this.map.setMode(EDIT);
        return komoo.event.trigger(this.map, 'drawing_started', this.feature);
      };

      DrawingManager.prototype.drawFeature = function(feature) {
        this.feature = feature;
        if (this.enabled === false) return;
        this.editFeature(this.feature);
        return this.map.setMode(NEW);
      };

      return DrawingManager;

    })();
    DrawingControl = (function(_super) {

      __extends(DrawingControl, _super);

      DrawingControl.prototype.id = "map-drawing-box";

      DrawingControl.prototype["class"] = "map-panel";

      DrawingControl.prototype.position = google.maps.ControlPosition.TOP_LEFT;

      function DrawingControl() {
        DrawingControl.__super__.constructor.call(this);
        this.box.hide();
        this.box.html("<div id=\"drawing-control\">\n  <div class=\"map-panel-title\" id=\"drawing-control-title\"></div>\n  <div class=\"content\" id=\"drawing-control-content\"></div>\n  <div class=\"map-panel-buttons\">\n    <div class=\"map-button\" id=\"drawing-control-finish\">" + (gettext('Next Step')) + "</div>\n    <div class=\"map-button\" id=\"drawing-control-cancel\">" + (gettext('Cancel')) + "</div>\n  </div>\n</div>");
        this.handleBoxEvents();
      }

      DrawingControl.prototype.handleMapEvents = function() {
        var _this = this;
        komoo.event.addListener(this.map, 'drawing_started', function(feature) {
          return _this.open(feature);
        });
        komoo.event.addListener(this.map, 'drawing_finished', function(feature) {
          return _this.close();
        });
        return komoo.event.addListener(this.map, 'mode_changed', function(mode) {
          return _this.setMode(mode);
        });
      };

      DrawingControl.prototype.handleBoxEvents = function() {
        var _this = this;
        $("#drawing-control-finish", this.box).click(function() {
          if ($("#drawing-control-finish", _this.box).hasClass('disabled')) return;
          return komoo.event.trigger(_this.map, 'finish_drawing');
        });
        return $("#drawing-control-cancel", this.box).click(function() {
          return komoo.event.trigger(_this.map, 'cancel_drawing');
        });
      };

      DrawingControl.prototype.handleButtonEvents = function() {
        var _this = this;
        $("#drawing-control-add", this.box).click(function() {
          return _this.map.setMode(_this.mode !== ADD ? ADD : EDIT);
        });
        $("#drawing-control-cutout", this.box).click(function() {
          return _this.map.setMode(_this.mode !== CUTOUT ? CUTOUT : EDIT);
        });
        return $("#drawing-control-delete", this.box).click(function() {
          return _this.map.setMode(_this.mode !== DELETE ? DELETE : EDIT);
        });
      };

      DrawingControl.prototype.setMode = function(mode) {
        var _ref;
        this.mode = mode;
        if (this.mode === NEW) {
          $("#drawing-control-content", this.box).hide();
          $("#drawing-control-finish", this.box).addClass('disabled');
        } else {
          $("#drawing-control-content", this.box).show();
          $("#drawing-control-finish", this.box).removeClass('disabled');
        }
        $(".map-button.active", this.box).removeClass("active");
        return $("#drawing-control-" + ((_ref = this.mode) != null ? _ref.toLowerCase() : void 0), this.box).addClass("active");
      };

      DrawingControl.prototype.getTitle = function() {
        var geometry, title, _ref, _ref2;
        if (this.feature.getGeometryType() === komoo.geometries.types.POLYGON) {
          geometry = 'polygon';
          title = gettext('Add shape');
        } else if ((_ref = this.feature.getGeometryType()) === komoo.geometries.types.LINESTRING || _ref === komoo.geometries.types.MULTILINESTRING) {
          geometry = 'linestring';
          title = gettext('Add line');
        } else if ((_ref2 = this.feature.getGeometryType()) === komoo.geometries.types.POINT || _ref2 === komoo.geometries.types.MULTIPOINT) {
          geometry = 'point';
          title = gettext('Add point');
        }
        return "<i class=\"icon-" + geometry + " middle\"></i><span class=\"middle\">" + title + "</span>";
      };

      DrawingControl.prototype.getContent = function() {
        var add, content, cutout, remove;
        add = $("<div class=\"map-button\" id=\"drawing-control-add\"><i class=\"icon-komoo-plus middle\"></i><span class=\"middle\">" + (gettext('Sum')) + "</span></div>");
        cutout = $("<div class=\"map-button\" id=\"drawing-control-cutout\"><i class=\"icon-komoo-minus middle\"></i><span class=\"middle\">" + (gettext('Cut out')) + "</span></div>");
        remove = $("<div class=\"map-button\" id=\"drawing-control-delete\"><i class=\"icon-komoo-trash middle\"></i></div>");
        content = $("<div>").addClass(this.feature.getGeometryType().toLowerCase());
        content.append(add);
        if (this.feature.getGeometryType() === komoo.geometries.types.POLYGON) {
          content.append(cutout);
        }
        content.append(remove);
        return content;
      };

      DrawingControl.prototype.open = function(feature) {
        this.feature = feature;
        $("#drawing-control-title", this.box).html(this.getTitle());
        $("#drawing-control-content", this.box).html(this.getContent());
        this.handleButtonEvents();
        return this.box.show();
      };

      DrawingControl.prototype.close = function() {
        return this.box.hide();
      };

      return DrawingControl;

    })(Box);
    PerimeterSelector = (function() {

      PerimeterSelector.prototype.enabled = true;

      function PerimeterSelector() {
        var _this = this;
        this.circle = new google.maps.Circle({
          visible: true,
          radius: 100,
          fillColor: "white",
          fillOpacity: 0.0,
          strokeColor: "#ffbda8",
          zIndex: -1
        });
        komoo.event.addListener(this.circle, 'click', function(e) {
          if (_this.map.mode === PERIMETER_SELECTION) {
            return _this.selected(e.latLng);
          }
        });
      }

      PerimeterSelector.prototype.select = function(radius, callback) {
        this.radius = radius;
        this.callback = callback;
        if (!this.enabled) return;
        this.origMode = this.map.mode;
        this.map.disableComponents('infoWindow');
        return this.map.setMode(PERIMETER_SELECTION);
      };

      PerimeterSelector.prototype.selected = function(latLng) {
        if (typeof this.radius === "number") this.circle.setRadius(this.radius);
        if (typeof this.callback === "function") {
          this.callback(latLng, this.circle);
        }
        this.circle.setCenter(latLng);
        this.circle.setMap(this.map.googleMap);
        komoo.event.trigger(this.map, 'perimeter_selected', latLng, this.circle);
        this.map.setMode(this.origMode);
        return this.map.enableComponents('infoWindow');
      };

      PerimeterSelector.prototype.handleMapEvents = function() {
        var eventName, _i, _len, _ref, _results,
          _this = this;
        komoo.event.addListener(this.map, 'select_perimeter', function(radius, callback) {
          return _this.select(radius, callback);
        });
        _ref = ['click', 'feature_click'];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          eventName = _ref[_i];
          _results.push(komoo.event.addListener(this.map, eventName, function(e) {
            if (_this.map.mode === PERIMETER_SELECTION) {
              return _this.selected(e.latLng);
            }
          }));
        }
        return _results;
      };

      PerimeterSelector.prototype.setMap = function(map) {
        this.map = map;
        return this.handleMapEvents();
      };

      PerimeterSelector.prototype.enable = function() {
        return this.enabled = true;
      };

      PerimeterSelector.prototype.disable = function() {
        this.hide();
        return this.enabled = false;
      };

      return PerimeterSelector;

    })();
    Balloon = (function() {

      Balloon.prototype.defaultWidth = "300px";

      Balloon.prototype.enabled = true;

      function Balloon(options) {
        this.options = options != null ? options : {};
        this.width = this.options.width || this.defaultWidth;
        this.createInfoBox(this.options);
        if (this.options.map) this.setMap(this.options.map);
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

      Balloon.prototype.handleMapEvents = function() {
        var _this = this;
        komoo.event.addListener(this.map, 'drawing_started', function(feature) {
          return _this.disable();
        });
        return komoo.event.addListener(this.map, 'drawing_finished', function(feature) {
          return _this.enable();
        });
      };

      Balloon.prototype.setInfoBox = function(infoBox) {
        this.infoBox = infoBox;
      };

      Balloon.prototype.setMap = function(map) {
        this.map = map;
        return this.handleMapEvents();
      };

      Balloon.prototype.enable = function() {
        return this.enabled = true;
      };

      Balloon.prototype.disable = function() {
        this.close(false);
        return this.enabled = false;
      };

      Balloon.prototype.open = function(options) {
        var empty, newPosition, point, position, _ref, _ref2, _ref3, _ref4;
        this.options = options != null ? options : {};
        if (!this.enabled) return;
        this.setContent(options.content || (options.features ? this.createClusterContent(options) : this.createFeatureContent(options)));
        this.feature = (_ref = options.feature) != null ? _ref : (_ref2 = options.features) != null ? _ref2.getAt(0) : void 0;
        position = (_ref3 = options.position) != null ? _ref3 : this.feature.getCenter();
        if (position instanceof Array) {
          empty = new komoo.geometries.Empty();
          position = empty.getLatLngFromArray(position);
        }
        point = komoo.utils.latLngToPoint(this.map, position);
        point.x += 5;
        newPosition = komoo.utils.pointToLatLng(this.map, point);
        this.infoBox.setPosition(newPosition);
        return this.infoBox.open((_ref4 = this.map.googleMap) != null ? _ref4 : this.map);
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
        this.title.html(content.url ? "<a href=\"" + content.url + "'\">" + content.title + "</a>" : content.title);
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
          title = feature.getProperty("type" === "OrganizationBranch" && feature.getProperty("organization_name")) ? feature.getProperty("organization_name") + " - " + feature.getProperty("name") : feature.getProperty("name");
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
        if (!(feature.getProperty("id") != null)) {
          return AjaxBalloon.__super__.createFeatureContent.call(this, options);
        }
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

      InfoWindow.prototype.open = function(options) {
        var _ref, _ref2;
        if ((_ref = this.feature) != null) _ref.displayTooltip = true;
        InfoWindow.__super__.open.call(this, options);
        return (_ref2 = this.feature) != null ? _ref2.displayTooltip = false : void 0;
      };

      InfoWindow.prototype.close = function(enableTooltip) {
        var _ref;
        if (enableTooltip == null) enableTooltip = true;
        if ((_ref = this.feature) != null) _ref.displayTooltip = true;
        if (enableTooltip) this.map.enableComponents('tooltip');
        return InfoWindow.__super__.close.call(this);
      };

      InfoWindow.prototype.customize = function() {
        var _this = this;
        InfoWindow.__super__.customize.call(this);
        return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
          var closeBox, div;
          div = _this.content.get(0);
          closeBox = _this.infoBox.div_.firstChild;
          google.maps.event.addDomListener(div, "mousemove", function(e) {
            return _this.map.disableComponents('tooltip');
          });
          google.maps.event.addDomListener(div, "mouseout", function(e) {
            closeBox = _this.infoBox.div_.firstChild;
            if (e.toElement !== closeBox) {
              return _this.map.enableComponents('tooltip');
            }
          });
          return google.maps.event.addDomListener(closeBox, "click", function(e) {
            return _this.close();
          });
        });
      };

      InfoWindow.prototype.handleMapEvents = function() {
        var _this = this;
        InfoWindow.__super__.handleMapEvents.call(this);
        komoo.event.addListener(this.map, 'feature_click', function(e, feature) {
          return setTimeout(function() {
            return _this.open({
              feature: feature,
              position: e.latLng
            });
          }, 200);
        });
        return komoo.event.addListener(this.map, 'feature_highlight_changed', function(e, feature) {
          return _this.open({
            feature: feature
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

      Tooltip.prototype.close = function() {
        clearTimeout(this.timer);
        return Tooltip.__super__.close.call(this);
      };

      Tooltip.prototype.customize = function() {
        var _this = this;
        Tooltip.__super__.customize.call(this);
        return google.maps.event.addDomListener(this.infoBox, "domready", function(e) {
          var closeBox, div;
          div = _this.infoBox.div_;
          google.maps.event.addDomListener(div, "click", function(e) {
            e.latLng = _this.infoBox.getPosition();
            return komoo.event.trigger(_this.map, 'feature_click', e, _this.feature);
          });
          closeBox = div.firstChild;
          return $(closeBox).hide();
        });
      };

      Tooltip.prototype.handleMapEvents = function() {
        var _this = this;
        Tooltip.__super__.handleMapEvents.call(this);
        komoo.event.addListener(this.map, 'feature_mousemove', function(e, feature) {
          var delay;
          clearTimeout(_this.timer);
          if (feature === _this.feature || !feature.displayTooltip) return;
          delay = feature.getType() === 'Community' ? 400 : 10;
          return _this.timer = setTimeout(function() {
            if (!feature.displayTooltip) return;
            return _this.open({
              feature: feature,
              position: e.latLng
            });
          }, delay);
        });
        komoo.event.addListener(this.map, 'feature_mouseout', function(e, feature) {
          return _this.close();
        });
        komoo.event.addListener(this.map, 'feature_click', function(e, feature) {
          return _this.close();
        });
        komoo.event.addListener(this.map, 'cluster_mouseover', function(features, position) {
          if (!features.getAt(0).displayTooltip) return;
          return _this.open({
            features: features,
            position: position
          });
        });
        komoo.event.addListener(this.map, 'cluster_mouseout', function(e, feature) {
          return _this.close();
        });
        return komoo.event.addListener(this.map, 'cluster_click', function(e, feature) {
          return _this.close();
        });
      };

      return Tooltip;

    })(AjaxBalloon);
    FeatureClusterer = (function() {

      FeatureClusterer.prototype.enabled = true;

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
        this.featureType = this.options.featureType;
        this.features = [];
        if (this.options.map) this.setMap(this.options.map);
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
            komoo.event.trigger(_this, eventName, features, c.getCenter());
            return komoo.event.trigger(_this.map, "cluster_" + eventName, features, c.getCenter());
          });
        });
      };

      FeatureClusterer.prototype.setMap = function(map) {
        this.map = map;
        this.initMarkerClusterer(this.options);
        this.initEvents();
        this.addFeatures(this.map.getFeatures());
        return this.handleMapEvents();
      };

      FeatureClusterer.prototype.handleMapEvents = function() {
        var _this = this;
        return komoo.event.addListener(this.map, 'feature_created', function(feature) {
          if (feature.getType() === _this.featureType) return _this.push(feature);
        });
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
    Location = (function() {

      Location.prototype.enabled = true;

      function Location() {
        this.geocoder = new google.maps.Geocoder();
      }

      Location.prototype.handleMapEvents = function() {
        var _this = this;
        komoo.event.addListener(this.map, 'goto', function(position, marker) {
          return _this.goTo(position, marker);
        });
        return komoo.event.addListener(this.map, 'goto_user_location', function() {
          return _this.goToUserLocation();
        });
      };

      Location.prototype.goTo = function(position, marker) {
        var latLng, request, _go,
          _this = this;
        if (marker == null) marker = true;
        _go = function(latLng) {
          if (latLng) {
            _this.map.googleMap.panTo(latLng);
            if (!_this.searchMarker) {
              _this.searchMarker = new google.maps.Marker();
              _this.searchMarker.setMap(_this.googleMap);
            }
            if (marker) return _this.searchMarker.setPosition(latLng);
          }
        };
        if (typeof position === "string") {
          request = {
            address: position,
            region: this.region
          };
          return this.geocoder.geocode(request, function(result, status_) {
            var first_result, latLng;
            if (status_ === google.maps.GeocoderStatus.OK) {
              first_result = result[0];
              latLng = first_result.geometry.location;
              return _go(latLng);
            }
          });
        } else {
          if (position instanceof Array) {
            latLng = new google.maps.LatLng(position[0], position[1]);
          } else {
            latLng = position;
          }
          return _go(latLng);
        }
      };

      Location.prototype.goToUserLocation = function() {
        var clientLocation, pos,
          _this = this;
        clientLocation = google.loader.ClientLocation;
        if (clientLocation) {
          pos = new google.maps.LatLng(clientLocation.latitude, clientLocation.longitude);
          this.map.googleMap.setCenter(pos);
          if (typeof console !== "undefined" && console !== null) {
            console.log('Getting location from Google...');
          }
        }
        if (navigator.geolocation) {
          return navigator.geolocation.getCurrentPosition(function(position) {
            pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            _this.map.googleMap.setCenter(pos);
            return typeof console !== "undefined" && console !== null ? console.log('Getting location from navigator.geolocation...') : void 0;
          }, function() {
            return typeof console !== "undefined" && console !== null ? console.log('User denied access to navigator.geolocation...') : void 0;
          });
        }
      };

      Location.prototype.setMap = function(map) {
        this.map = map;
        return this.handleMapEvents();
      };

      Location.prototype.enable = function() {
        return this.enabled = true;
      };

      Location.prototype.disable = function() {
        this.close(false);
        return this.enabled = false;
      };

      return Location;

    })();
    SaveLocation = (function(_super) {

      __extends(SaveLocation, _super);

      function SaveLocation() {
        SaveLocation.__super__.constructor.apply(this, arguments);
      }

      SaveLocation.prototype.handleMapEvents = function() {
        var _this = this;
        SaveLocation.__super__.handleMapEvents.call(this);
        komoo.event.addListener(this.map, 'save_location', function(center, zoom) {
          return _this.saveLocation(center, zoom);
        });
        return komoo.event.addListener(this.map, 'goto_saved_location', function() {
          return _this.goToSavedLocation();
        });
      };

      SaveLocation.prototype.saveLocation = function(center, zoom) {
        if (center == null) center = this.map.googleMap.getCenter();
        if (zoom == null) zoom = this.map.getZoom();
        komoo.utils.createCookie('lastLocation', center.toUrlValue(), 90);
        return komoo.utils.createCookie('lastZoom', zoom, 90);
      };

      SaveLocation.prototype.goToSavedLocation = function() {
        var center, lastLocation, zoom;
        lastLocation = komoo.utils.readCookie('lastLocation');
        zoom = parseInt(komoo.utils.readCookie('lastZoom'), 10);
        if (lastLocation && zoom) {
          if (typeof console !== "undefined" && console !== null) {
            console.log('Getting location from cookie...');
          }
          lastLocation = lastLocation.split(',');
          center = new google.maps.LatLng(lastLocation[0], lastLocation[1]);
          this.map.googleMap.setCenter(center);
          return this.map.googleMap.setZoom(zoom);
        }
      };

      return SaveLocation;

    })(Location);
    AutosaveLocation = (function(_super) {

      __extends(AutosaveLocation, _super);

      function AutosaveLocation() {
        AutosaveLocation.__super__.constructor.apply(this, arguments);
      }

      AutosaveLocation.prototype.handleMapEvents = function() {
        var _this = this;
        AutosaveLocation.__super__.handleMapEvents.call(this);
        return komoo.event.addListener(this.map, 'idle', function() {
          return _this.saveLocation();
        });
      };

      return AutosaveLocation;

    })(SaveLocation);
    StreetView = (function() {

      StreetView.prototype.enabled = true;

      function StreetView() {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Initializing StreetView support.");
        }
        this.streetViewPanel = $("<div>").addClass("map-panel");
        this.streetViewPanel.height("100%").width("50%");
        this.streetViewPanel.hide();
        this.createObject();
      }

      StreetView.prototype.setMap = function(map) {
        this.map = map;
        this.map.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(this.streetViewPanel.get(0));
        if (this.streetView != null) {
          return this.map.googleMap.setStreetView(this.streetView);
        }
      };

      StreetView.prototype.createObject = function() {
        var options, _ref,
          _this = this;
        options = {
          enableCloseButton: true,
          visible: false
        };
        this.streetView = new google.maps.StreetViewPanorama(this.streetViewPanel.get(0), options);
        if ((_ref = this.map) != null) {
          _ref.googleMap.setStreetView(this.streetView);
        }
        return google.maps.event.addListener(this.streetView, "visible_changed", function() {
          if (_this.streetView.getVisible()) {
            return _this.streetViewPanel.show();
          } else {
            return _this.streetViewPanel.hide();
          }
        });
      };

      return StreetView;

    })();
    return window.komoo.controls = {
      DrawingManager: DrawingManager,
      Balloon: Balloon,
      AjaxBalloon: AjaxBalloon,
      InfoWindow: InfoWindow,
      Tooltip: Tooltip,
      FeatureClusterer: FeatureClusterer,
      SupporterBox: SupporterBox,
      LicenseBox: LicenseBox,
      PerimeterSelector: PerimeterSelector,
      Location: Location,
      SaveLocation: SaveLocation,
      AutosaveLocation: AutosaveLocation,
      StreetView: StreetView,
      makeDrawingManager: function(options) {
        return new DrawingManager(options);
      },
      makeDrawingControl: function(options) {
        return new DrawingControl(options);
      },
      makeInfoWindow: function(options) {
        return new InfoWindow(options);
      },
      makeTooltip: function(options) {
        return new Tooltip(options);
      },
      makeFeatureClusterer: function(options) {
        return new FeatureClusterer(options);
      },
      makeSupporterBox: function(options) {
        return new SupporterBox(options);
      },
      makeLicenseBox: function(options) {
        return new LicenseBox(options);
      },
      makePerimeterSelector: function(options) {
        return new PerimeterSelector(options);
      },
      makeLocation: function(options) {
        return new Location(options);
      },
      makeSaveLocation: function(options) {
        return new SaveLocation(options);
      },
      makeAutosaveLocation: function(options) {
        return new AutosaveLocation(options);
      },
      makeStreetView: function(options) {
        return new StreetView(options);
      }
    };
  });

}).call(this);
