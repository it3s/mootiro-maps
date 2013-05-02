(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  define(function(require) {
    'use strict';
    var ADD, AjaxBalloon, AutosaveLocation, AutosaveMapType, Balloon, Box, CUTOUT, CloseBox, Component, DELETE, DrawingControl, DrawingManager, EDIT, EMPTY, FeatureClusterer, FeatureFilter, FeatureZoomFilter, GeometrySelector, InfoBox, InfoWindow, LINESTRING, LicenseBox, LoadingBox, Location, MULTILINESTRING, MULTIPOINT, MULTIPOLYLINE, MarkerClusterer, NEW, OVERLAY, PERIMETER_SELECTION, POINT, POLYGON, POLYLINE, PerimeterSelector, SaveLocation, SaveMapType, SearchBox, StreetView, SupporterBox, Tooltip, common, geometries, googleMaps, utils, _ADD_LINE, _ADD_POINT, _ADD_SHAPE, _CANCEL, _CLOSE, _CUT_OUT, _LOADING, _NEXT_STEP, _SUM, _base;
    googleMaps = require('googlemaps');
    Component = require('./component');
    common = require('./common');
    geometries = require('./geometries');
    utils = require('./utils');
    InfoBox = require('infobox');
    MarkerClusterer = require('markerclusterer');
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
    _NEXT_STEP = gettext('Next Step');
    _CANCEL = gettext('Cancel');
    _CLOSE = gettext('Close');
    _ADD_SHAPE = gettext('Add shape');
    _ADD_LINE = gettext('Add line');
    _ADD_POINT = gettext('Add point');
    _SUM = gettext('Sum');
    _CUT_OUT = gettext('Cut out');
    _LOADING = gettext('Loading...');
    EMPTY = common.geometries.types.EMPTY;
    POINT = common.geometries.types.POINT;
    MULTIPOINT = common.geometries.types.MULTIPOINT;
    POLYGON = common.geometries.types.POLYGON;
    POLYLINE = common.geometries.types.LINESTRING;
    LINESTRING = common.geometries.types.LINESTRING;
    MULTIPOLYLINE = common.geometries.types.MULTILINESTRING;
    MULTILINESTRING = common.geometries.types.MULTILINESTRING;
    OVERLAY = {};
    OVERLAY[POINT] = googleMaps.drawing.OverlayType.MARKER;
    OVERLAY[MULTIPOINT] = googleMaps.drawing.OverlayType.MARKER;
    OVERLAY[LINESTRING] = googleMaps.drawing.OverlayType.POLYLINE;
    OVERLAY[MULTILINESTRING] = googleMaps.drawing.OverlayType.POLYLINE;
    OVERLAY[POLYGON] = googleMaps.drawing.OverlayType.POLYGON;
    EDIT = 'edit';
    DELETE = 'delete';
    NEW = 'new';
    ADD = 'add';
    CUTOUT = 'cutout';
    PERIMETER_SELECTION = 'perimeter_selection';
    Box = (function(_super) {

      __extends(Box, _super);

      function Box() {
        Box.__super__.constructor.apply(this, arguments);
      }

      Box.prototype.position = googleMaps.ControlPosition.RIGHT_BOTTOM;

      Box.prototype.init = function() {
        Box.__super__.init.call(this);
        this.box = $("<div>");
        if (this.id != null) this.box.attr("id", this.id);
        if (this["class"] != null) this.box.addClass(this["class"]);
        this.map.addControl(this.position, this.box.get(0));
        return typeof this.handleMapEvents === "function" ? this.handleMapEvents() : void 0;
      };

      Box.prototype.hide = function() {
        return this.box.hide();
      };

      Box.prototype.show = function() {
        return this.box.show();
      };

      return Box;

    })(Component);
    LoadingBox = (function(_super) {

      __extends(LoadingBox, _super);

      function LoadingBox() {
        LoadingBox.__super__.constructor.apply(this, arguments);
      }

      LoadingBox.prototype.position = googleMaps.ControlPosition.TOP_CENTER;

      LoadingBox.prototype.id = 'map-loading';

      LoadingBox.prototype.init = function() {
        LoadingBox.__super__.init.call(this);
        this.requestsTotal = 0;
        this.requestsWaiting = 0;
        this.repaint();
        return this.hide();
      };

      LoadingBox.prototype.getPercent = function() {
        if (this.requestsTotal === 0) return 0;
        return Math.round(100 * ((this.requestsTotal - this.requestsWaiting) / this.requestsTotal));
      };

      LoadingBox.prototype.repaint = function() {
        return this.box.html("" + _LOADING + " " + (this.getPercent()) + "%");
      };

      LoadingBox.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('features_request_started', function() {
          return _this.displayTimer = setTimeout(function() {
            return _this.show();
          }, 500);
        });
        this.map.subscribe('features_request_queued', function() {
          _this.requestsTotal++;
          _this.requestsWaiting++;
          return _this.repaint();
        });
        this.map.subscribe('features_request_unqueued', function() {
          _this.requestsWaiting--;
          return _this.repaint();
        });
        return this.map.subscribe('features_request_completed', function() {
          _this.requestsTotal = 0;
          _this.requestsWaiting = 0;
          clearTimeout(_this.displayTimer);
          return setTimeout(function() {
            return _this.hide();
          }, 200);
        });
      };

      return LoadingBox;

    })(Box);
    SearchBox = (function(_super) {

      __extends(SearchBox, _super);

      function SearchBox() {
        SearchBox.__super__.constructor.apply(this, arguments);
      }

      SearchBox.prototype.position = googleMaps.ControlPosition.TOP_RIGHT;

      SearchBox.prototype.id = 'map-searchbox';

      SearchBox.prototype.init = function() {
        var _this = this;
        SearchBox.__super__.init.call(this);
        return require(['map/views'], function(Views) {
          _this.view = new Views.SearchBoxView();
          _this.box.append(_this.view.render().el);
          return _this.handleViewEvents();
        });
      };

      SearchBox.prototype.handleViewEvents = function() {
        var _this = this;
        return this.view.on('search', function(location) {
          var position, type;
          type = location.type;
          position = location.position;
          return _this.map.publish('goto', position, true);
        });
      };

      return SearchBox;

    })(Box);
    SupporterBox = (function(_super) {

      __extends(SupporterBox, _super);

      function SupporterBox() {
        SupporterBox.__super__.constructor.apply(this, arguments);
      }

      SupporterBox.prototype.id = "map-supporters";

      SupporterBox.prototype.init = function() {
        SupporterBox.__super__.init.call(this);
        return this.box.append($("#map-supporters-content").show());
      };

      return SupporterBox;

    })(Box);
    LicenseBox = (function(_super) {

      __extends(LicenseBox, _super);

      function LicenseBox() {
        LicenseBox.__super__.constructor.apply(this, arguments);
      }

      LicenseBox.prototype.id = "map-license";

      LicenseBox.prototype.position = googleMaps.ControlPosition.BOTTOM_LEFT;

      LicenseBox.prototype.init = function() {
        LicenseBox.__super__.init.call(this);
        return this.box.html('Este conteúdo é disponibilizado nos termos da licença <a href="http://creativecommons.org/licenses/by-sa/3.0/deed.pt_BR">Creative Commons - Atribuição - Partilha nos Mesmos Termos 3.0 Não Adaptada</a>; pode estar sujeito a condições adicionais. Para mais detalhes, consulte as Condições de Uso.');
      };

      return LicenseBox;

    })(Box);
    DrawingManager = (function(_super) {

      __extends(DrawingManager, _super);

      function DrawingManager() {
        DrawingManager.__super__.constructor.apply(this, arguments);
      }

      DrawingManager.prototype.enabled = true;

      DrawingManager.prototype.defaultDrawingManagerOptions = {
        drawingControl: false,
        drawingMode: null
      };

      DrawingManager.prototype.componentOriginalStatus = {};

      DrawingManager.prototype.init = function(options) {
        var _base2;
        this.options = options != null ? options : {};
        if ((_base2 = this.options).drawingManagerOptions == null) {
          _base2.drawingManagerOptions = this.defaultDrawingManagerOptions;
        }
        if (this.options.map) return this.setMap(this.options.map);
      };

      DrawingManager.prototype.initManager = function(options) {
        if (options == null) options = this.defaultDrawingManagerOptions;
        this.manager = new googleMaps.drawing.DrawingManager(options);
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
        this.manager.setDrawingMode(((_ref = this.mode) === ADD || _ref === NEW) || (this.mode === CUTOUT && this.feature.getGeometryType() === POLYGON) ? OVERLAY[this.feature.getGeometryType()] : null);
        if (this.mode === CUTOUT && this.feature.getGeometryType() !== POLYGON) {
          return this.mode = EDIT;
        }
      };

      DrawingManager.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('draw_feature', function(geometryType, feature) {
          return _this.drawFeature(feature);
        });
        this.map.subscribe('edit_feature', function(feature) {
          return _this.editFeature(feature);
        });
        this.map.subscribe('drawing_finished', function(feature) {
          _this.feature.setEditable(false);
          _this.feature.updateIcon();
          _this.setFeature(null);
          return _this.setMode(null);
        });
        this.map.subscribe('finish_drawing', function() {
          return _this.map.publish('drawing_finished', _this.feature, true);
        });
        this.map.subscribe('cancel_drawing', function() {
          return _this.map.publish('drawing_finished', _this.feature, false);
        });
        this.map.subscribe('mode_changed', function(mode) {
          return _this.setMode(mode);
        });
        return this.map.subscribe('feature_rightclick', function(e, feature) {
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
              sArea = googleMaps.geometry.spherical.computeSignedArea(path);
              sAreaAdded = googleMaps.geometry.spherical.computeSignedArea(paths.getAt(0));
              orientation = sArea / Math.abs(sArea);
              orientationAdded = sAreaAdded / Math.abs(sAreaAdded);
              if ((orientation === orientationAdded && _this.mode === CUTOUT) || (orientation !== orientationAdded && ((_ref4 = _this.mode) === ADD || _ref4 === NEW))) {
                path = new googleMaps.MVCArray(path.getArray().reverse());
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
            if (_this.feature.getGeometryType() === POLYGON) {
              paths = _this.feature.getGeometry().getPaths();
              paths.forEach(function(path, index) {
                if (utils.isPointInside(e.latLng, path)) {
                  return paths.removeAt(index);
                }
              });
            } else if (o && _this.feature.getGeometryType() === MULTIPOINT) {
              markers = _this.feature.getGeometry().getMarkers();
              index = $.inArray(o, markers.getArray());
              if (index > -1) {
                marker = markers.removeAt(index);
                marker.setMap(null);
              }
            } else if (o && _this.feature.getGeometryType() === MULTILINESTRING) {
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
        if (this.feature.getGeometryType() === 'Empty') {
          this.map.publish('select_new_geometry', this.feature);
          return;
        }
        this.feature.setEditable(true);
        options = {};
        options["" + OVERLAY[this.feature.getGeometryType()] + "Options"] = this.feature.getGeometry().getOverlayOptions({
          strokeWeight: 2.5,
          zoom: 100
        });
        this.manager.setOptions(options);
        this.map.setMode(EDIT);
        return this.map.publish('drawing_started', this.feature);
      };

      DrawingManager.prototype.drawFeature = function(feature) {
        this.feature = feature;
        if (this.enabled === false) return;
        this.editFeature(this.feature);
        return this.map.setMode(NEW);
      };

      return DrawingManager;

    })(Component);
    CloseBox = (function(_super) {

      __extends(CloseBox, _super);

      function CloseBox() {
        CloseBox.__super__.constructor.apply(this, arguments);
      }

      CloseBox.prototype.id = "map-drawing-box";

      CloseBox.prototype["class"] = "map-panel";

      CloseBox.prototype.position = googleMaps.ControlPosition.TOP_LEFT;

      CloseBox.prototype.init = function(opt) {
        var title, _ref;
        if (opt == null) {
          opt = {
            title: ''
          };
        }
        CloseBox.__super__.init.call(this);
        title = (_ref = opt.title) != null ? _ref : '';
        this.box.html("<div id=\"drawing-control\">\n  <div class=\"map-panel-title\" id=\"drawing-control-title\">" + title + "</div>\n  <div class=\"content\" id=\"drawing-control-content\"></div>\n  <div class=\"map-panel-buttons\">\n    <div class=\"map-button\" id=\"drawing-control-cancel\">" + _CLOSE + "</div>\n  </div>\n</div>");
        this.show();
        return this.handleButtonEvents();
      };

      CloseBox.prototype.setTitle = function(title) {
        if (title == null) title = '';
        return this.box.find('#drawing-control-title').text(title);
      };

      CloseBox.prototype.handleButtonEvents = function() {
        var _this = this;
        return $("#drawing-control-cancel", this.box).click(function() {
          return _this.map.publish('close_clicked');
        });
      };

      return CloseBox;

    })(Box);
    GeometrySelector = (function(_super) {

      __extends(GeometrySelector, _super);

      function GeometrySelector() {
        GeometrySelector.__super__.constructor.apply(this, arguments);
      }

      GeometrySelector.prototype.id = "map-drawing-box";

      GeometrySelector.prototype["class"] = "map-panel";

      GeometrySelector.prototype.position = googleMaps.ControlPosition.TOP_LEFT;

      GeometrySelector.prototype.init = function() {
        GeometrySelector.__super__.init.call(this);
        this.hide();
        this.box.html("<div id=\"geometry-selector\">\n  <div class=\"map-panel-title\" id=\"drawing-control-title\"></div>\n  <ul class=\"content\" id=\"drawing-control-content\">\n    <li class=\"polygon btn\" data-geometry-type=\"Polygon\">\n      <i class=\"icon-polygon middle\"></i><span class=\"middle\">Adicionar área</span>\n    </li>\n    <li class=\"linestring btn\" data-geometry-type=\"LineString\">\n      <i class=\"icon-linestring middle\"></i><span class=\"middle\">Adicionar linha</span>\n    </li>\n    <li class=\"point btn\" data-geometry-type=\"Point\">\n      <i class=\"icon-point middle\"></i><span class=\"middle\">Adicionar ponto</span>\n    </li>\n  </ul>\n  <div class=\"map-panel-buttons\">\n    <div class=\"map-button\" id=\"drawing-control-cancel\">" + _CANCEL + "</div>\n  </div>\n</div>");
        return this.handleBoxEvents();
      };

      GeometrySelector.prototype.handleMapEvents = function() {
        var _this = this;
        return this.map.subscribe('select_new_geometry', function(feature) {
          return _this.open(feature);
        });
      };

      GeometrySelector.prototype.handleBoxEvents = function() {
        var _this = this;
        return this.box.find('li').each(function(i, element) {
          var $element, geometryType;
          $element = $(element);
          geometryType = $element.attr('data-geometry-type');
          return $element.click(function() {
            _this.close();
            return _this.map.editFeature(_this.feature, geometryType);
          });
        });
      };

      GeometrySelector.prototype.handleButtonEvents = function() {
        var _this = this;
        return $("#drawing-control-cancel", this.box).click(function() {
          return _this.map.publish('cancel_drawing');
        });
      };

      GeometrySelector.prototype.showContent = function() {
        var geometryType, _i, _len, _ref, _ref2, _results;
        this.box.find('li').hide();
        _ref2 = (_ref = this.feature.getFeatureType()) != null ? _ref.geometryTypes : void 0;
        _results = [];
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
          geometryType = _ref2[_i];
          _results.push(this.box.find("li." + (geometryType.toLowerCase())).show());
        }
        return _results;
      };

      GeometrySelector.prototype.open = function(feature) {
        this.feature = feature;
        this.showContent();
        $("#drawing-control-title", this.box).html('Selecione o tipo de objeto');
        this.handleButtonEvents();
        return this.show();
      };

      GeometrySelector.prototype.close = function() {
        return this.hide();
      };

      return GeometrySelector;

    })(Box);
    DrawingControl = (function(_super) {

      __extends(DrawingControl, _super);

      function DrawingControl() {
        DrawingControl.__super__.constructor.apply(this, arguments);
      }

      DrawingControl.prototype.id = "map-drawing-box";

      DrawingControl.prototype["class"] = "map-panel";

      DrawingControl.prototype.position = googleMaps.ControlPosition.TOP_LEFT;

      DrawingControl.prototype.init = function() {
        DrawingControl.__super__.init.call(this);
        this.hide();
        this.box.html("<div id=\"drawing-control\">\n  <div class=\"map-panel-title\" id=\"drawing-control-title\"></div>\n  <div class=\"content\" id=\"drawing-control-content\"></div>\n  <div class=\"map-panel-buttons\">\n    <div class=\"map-button\" id=\"drawing-control-finish\">" + _NEXT_STEP + "</div>\n    <div class=\"map-button\" id=\"drawing-control-cancel\">" + _CANCEL + "</div>\n  </div>\n</div>");
        return this.handleBoxEvents();
      };

      DrawingControl.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('drawing_started', function(feature) {
          return _this.open(feature);
        });
        this.map.subscribe('drawing_finished', function(feature) {
          return _this.close();
        });
        return this.map.subscribe('mode_changed', function(mode) {
          return _this.setMode(mode);
        });
      };

      DrawingControl.prototype.handleBoxEvents = function() {
        var _this = this;
        $("#drawing-control-finish", this.box).click(function() {
          if ($("#drawing-control-finish", _this.box).hasClass('disabled')) return;
          return _this.map.publish('finish_drawing');
        });
        return $("#drawing-control-cancel", this.box).click(function() {
          return _this.map.publish('cancel_drawing');
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
        if (this.feature.getGeometryType() === POLYGON) {
          geometry = 'polygon';
          title = _ADD_SHAPE;
        } else if ((_ref = this.feature.getGeometryType()) === LINESTRING || _ref === MULTILINESTRING) {
          geometry = 'linestring';
          title = _ADD_LINE;
        } else if ((_ref2 = this.feature.getGeometryType()) === POINT || _ref2 === MULTIPOINT) {
          geometry = 'point';
          title = _ADD_POINT;
        }
        return "<i class=\"icon-" + geometry + " middle\"></i><span class=\"middle\">" + title + "</span>";
      };

      DrawingControl.prototype.getContent = function() {
        var add, content, cutout, remove;
        add = $("<div class=\"map-button\" id=\"drawing-control-add\"><i class=\"icon-komoo-plus middle\"></i><span class=\"middle\">" + _SUM + "</span></div>");
        cutout = $("<div class=\"map-button\" id=\"drawing-control-cutout\"><i class=\"icon-komoo-minus middle\"></i><span class=\"middle\">" + _CUT_OUT + "</span></div>");
        remove = $("<div class=\"map-button\" id=\"drawing-control-delete\"><i class=\"icon-komoo-trash middle\"></i></div>");
        content = $("<div>").addClass(this.feature.getGeometryType().toLowerCase());
        if (this.feature.getGeometryType() !== POINT) content.append(add);
        if (this.feature.getGeometryType() === POLYGON) content.append(cutout);
        if (this.feature.getGeometryType() !== POINT) content.append(remove);
        return content;
      };

      DrawingControl.prototype.open = function(feature) {
        this.feature = feature;
        $("#drawing-control-title", this.box).html(this.getTitle());
        $("#drawing-control-content", this.box).html(this.getContent());
        this.handleButtonEvents();
        return this.show();
      };

      DrawingControl.prototype.close = function() {
        return this.hide();
      };

      return DrawingControl;

    })(Box);
    PerimeterSelector = (function(_super) {

      __extends(PerimeterSelector, _super);

      function PerimeterSelector() {
        PerimeterSelector.__super__.constructor.apply(this, arguments);
      }

      PerimeterSelector.prototype.enabled = true;

      PerimeterSelector.prototype.init = function() {
        var _this = this;
        PerimeterSelector.__super__.init.call(this);
        this.circle = new googleMaps.Circle({
          visible: true,
          radius: 100,
          fillColor: "white",
          fillOpacity: 0.0,
          strokeColor: "#ffbda8",
          zIndex: -1
        });
        this.marker = new googleMaps.Marker({
          icon: '/static/img/marker.png'
        });
        return komoo.event.addListener(this.circle, 'click', function(e) {
          if (_this.map.mode === PERIMETER_SELECTION) {
            return _this.selected(e.latLng);
          }
        });
      };

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
        this.marker.setPosition(latLng);
        this.marker.setMap(this.map.googleMap);
        this.map.publish('perimeter_selected', latLng, this.circle);
        this.map.setMode(this.origMode);
        return this.map.enableComponents('infoWindow');
      };

      PerimeterSelector.prototype.handleMapEvents = function() {
        var eventName, _i, _len, _ref, _results,
          _this = this;
        this.map.subscribe('select_perimeter', function(radius, callback) {
          return _this.select(radius, callback);
        });
        _ref = ['click', 'feature_click'];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          eventName = _ref[_i];
          _results.push(this.map.subscribe(eventName, function(e) {
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

    })(Component);
    Balloon = (function(_super) {

      __extends(Balloon, _super);

      function Balloon() {
        Balloon.__super__.constructor.apply(this, arguments);
      }

      Balloon.prototype.defaultWidth = "300px";

      Balloon.prototype.enabled = true;

      Balloon.prototype.init = function(options) {
        this.options = options != null ? options : {};
        Balloon.__super__.init.call(this);
        this.width = this.options.width || this.defaultWidth;
        this.createInfoBox(this.options);
        if (this.options.map) this.setMap(this.options.map);
        return this.customize();
      };

      Balloon.prototype.createInfoBox = function(options) {
        return this.setInfoBox(new InfoBox({
          pixelOffset: new googleMaps.Size(0, -20),
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
        this.map.subscribe('drawing_started', function(feature) {
          return _this.disable();
        });
        return this.map.subscribe('drawing_finished', function(feature) {
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
        this.setContent(this.options.content || (this.options.features ? this.createClusterContent(this.options) : this.createFeatureContent(this.options)));
        this.feature = (_ref = this.options.feature) != null ? _ref : (_ref2 = this.options.features) != null ? _ref2.getAt(0) : void 0;
        position = (_ref3 = this.options.position) != null ? _ref3 : this.feature.getCenter();
        if (position instanceof Array) {
          empty = new komoo.geometries.Empty();
          position = empty.getLatLngFromArray(position);
        }
        point = utils.latLngToPoint(this.map, position);
        point.x += 5;
        newPosition = utils.pointToLatLng(this.map, point);
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
        googleMaps.event.addDomListener(this.infoBox, "domready", function(e) {
          var div;
          div = _this.infoBox.div_;
          googleMaps.event.addDomListener(div, "click", function(e) {
            e.cancelBubble = true;
            return typeof e.stopPropagation === "function" ? e.stopPropagation() : void 0;
          });
          googleMaps.event.addDomListener(div, "mouseout", function(e) {
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
        if (feature) title = feature.getProperty("name");
        return {
          title: title,
          url: "",
          body: ""
        };
      };

      return Balloon;

    })(Component);
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
        return _LOADING;
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
        var _ref, _ref2;
        if (enableTooltip == null) enableTooltip = true;
        if ((_ref = this.feature) != null) _ref.setHighlight(false);
        if ((_ref2 = this.feature) != null) _ref2.displayTooltip = true;
        if (enableTooltip) this.map.enableComponents('tooltip');
        return InfoWindow.__super__.close.call(this);
      };

      InfoWindow.prototype.customize = function() {
        var _this = this;
        InfoWindow.__super__.customize.call(this);
        return googleMaps.event.addDomListener(this.infoBox, "domready", function(e) {
          var closeBox, div;
          div = _this.content.get(0);
          closeBox = _this.infoBox.div_.firstChild;
          googleMaps.event.addDomListener(div, "mousemove", function(e) {
            return _this.map.disableComponents('tooltip');
          });
          googleMaps.event.addDomListener(div, "mouseout", function(e) {
            closeBox = _this.infoBox.div_.firstChild;
            if (e.toElement !== closeBox) {
              return _this.map.enableComponents('tooltip');
            }
          });
          return googleMaps.event.addDomListener(closeBox, "click", function(e) {
            return _this.close();
          });
        });
      };

      InfoWindow.prototype.handleMapEvents = function() {
        var _this = this;
        InfoWindow.__super__.handleMapEvents.call(this);
        this.map.subscribe('feature_click', function(e, feature) {
          return setTimeout(function() {
            return _this.open({
              feature: feature,
              position: e.latLng
            });
          }, 200);
        });
        return this.map.subscribe('feature_highlight_changed', function(e, feature) {
          if (feature.isHighlighted()) {
            return _this.open({
              feature: feature
            });
          }
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
        return googleMaps.event.addDomListener(this.infoBox, "domready", function(e) {
          var closeBox, div;
          div = _this.infoBox.div_;
          googleMaps.event.addDomListener(div, "click", function(e) {
            e.latLng = _this.infoBox.getPosition();
            return _this.map.publish('feature_click', e, _this.feature);
          });
          closeBox = div.firstChild;
          return $(closeBox).hide();
        });
      };

      Tooltip.prototype.handleMapEvents = function() {
        var _this = this;
        Tooltip.__super__.handleMapEvents.call(this);
        this.map.subscribe('feature_mousemove', function(e, feature) {
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
        this.map.subscribe('feature_mouseout', function(e, feature) {
          return _this.close();
        });
        this.map.subscribe('feature_click', function(e, feature) {
          return _this.close();
        });
        this.map.subscribe('cluster_mouseover', function(features, position) {
          var _ref;
          if (!((_ref = features.getAt(0)) != null ? _ref.displayTooltip : void 0)) {
            return;
          }
          return _this.open({
            features: features,
            position: position
          });
        });
        this.map.subscribe('cluster_mouseout', function(e, feature) {
          return _this.close();
        });
        return this.map.subscribe('cluster_click', function(e, feature) {
          return _this.close();
        });
      };

      return Tooltip;

    })(AjaxBalloon);
    FeatureClusterer = (function(_super) {

      __extends(FeatureClusterer, _super);

      function FeatureClusterer() {
        FeatureClusterer.__super__.constructor.apply(this, arguments);
      }

      FeatureClusterer.prototype.enabled = true;

      FeatureClusterer.prototype.maxZoom = 9;

      FeatureClusterer.prototype.gridSize = 20;

      FeatureClusterer.prototype.minSize = 1;

      FeatureClusterer.prototype.imagePath = '/static/img/cluster/communities';

      FeatureClusterer.prototype.imageSizes = [24, 29, 35, 41, 47];

      FeatureClusterer.prototype.init = function(options) {
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
        if (this.options.map) return this.setMap(this.options.map);
      };

      FeatureClusterer.prototype.initMarkerClusterer = function(options) {
        var map, _ref;
        if (options == null) options = {};
        map = ((_ref = this.map) != null ? _ref.googleMap : void 0) || this.map;
        return window.clusterer = this.clusterer = new MarkerClusterer(map, [], options);
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
            return _this.map.publish("cluster_" + eventName, features, c.getCenter());
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
        this.map.subscribe('feature_created', function(feature) {
          if (_this.map.getZoom() <= _this.maxZoom && (!(_this.featureType != null) || feature.getType() === _this.featureType)) {
            return _this.push(feature);
          }
        });
        this.map.subscribe('idle features_loaded', function() {
          if (_this.map.getZoom() <= _this.maxZoom) {
            return _this.map.getFeatures().setVisible(false);
          } else {
            return _this.map.getFeatures().setVisible(true);
          }
        });
        this.map.subscribe('idle', function() {
          if (_this.length === 0 && _this.map.getZoom() <= _this.maxZoom) {
            return _this.addFeatures(_this.map.getFeatures());
          }
        });
        return this.map.subscribe('features_request_completed', function() {
          if (_this.map.getZoom() <= _this.maxZoom) {
            return _this.addFeatures(_this.map.getFeatures());
          }
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
          this.clusterer.addMarker(element.getMarker().getOverlay().markers_.getAt(0), true);
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
        if (features != null) {
          features.forEach(function(feature) {
            return _this.push(feature);
          });
        }
        return this.repaint();
      };

      return FeatureClusterer;

    })(Component);
    Location = (function(_super) {

      __extends(Location, _super);

      function Location() {
        Location.__super__.constructor.apply(this, arguments);
      }

      Location.prototype.enabled = true;

      Location.prototype.init = function() {
        this.geocoder = new googleMaps.Geocoder();
        return this.marker = new googleMaps.Marker({
          icon: '/static/img/marker.png'
        });
      };

      Location.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('goto', function(position, marker) {
          return _this.goTo(position, marker);
        });
        return this.map.subscribe('goto_user_location', function() {
          return _this.goToUserLocation();
        });
      };

      Location.prototype.goTo = function(position, marker) {
        var latLng, request, _go,
          _this = this;
        if (marker == null) marker = false;
        _go = function(latLng) {
          if (latLng) {
            _this.map.googleMap.panTo(latLng);
            if (marker) return _this.marker.setPosition(latLng);
          }
        };
        if (typeof position === "string") {
          request = {
            address: position,
            region: this.region
          };
          return this.geocoder.geocode(request, function(result, status_) {
            var first_result, latLng;
            if (status_ === googleMaps.GeocoderStatus.OK) {
              first_result = result[0];
              latLng = first_result.geometry.location;
              return _go(latLng);
            }
          });
        } else {
          latLng = position instanceof Array ? position.length === 2 ? new googleMaps.LatLng(position[0], position[1]) : void 0 : position;
          return _go(latLng);
        }
      };

      Location.prototype.goToUserLocation = function() {
        var clientLocation, pos,
          _this = this;
        clientLocation = google.loader.ClientLocation;
        if (clientLocation) {
          pos = new googleMaps.LatLng(clientLocation.latitude, clientLocation.longitude);
          this.map.googleMap.setCenter(pos);
          if (typeof console !== "undefined" && console !== null) {
            console.log('Getting location from Google...');
          }
        }
        if (navigator.geolocation) {
          return navigator.geolocation.getCurrentPosition(function(position) {
            pos = new googleMaps.LatLng(position.coords.latitude, position.coords.longitude);
            _this.map.googleMap.setCenter(pos);
            return typeof console !== "undefined" && console !== null ? console.log('Getting location from navigator.geolocation...') : void 0;
          }, function() {
            return typeof console !== "undefined" && console !== null ? console.log('User denied access to navigator.geolocation...') : void 0;
          });
        }
      };

      Location.prototype.setMap = function(map) {
        this.map = map;
        this.marker.setMap(this.map.googleMap);
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

    })(Component);
    SaveLocation = (function(_super) {

      __extends(SaveLocation, _super);

      function SaveLocation() {
        SaveLocation.__super__.constructor.apply(this, arguments);
      }

      SaveLocation.prototype.handleMapEvents = function() {
        var _this = this;
        SaveLocation.__super__.handleMapEvents.call(this);
        this.map.subscribe('save_location', function(center, zoom) {
          return _this.saveLocation(center, zoom);
        });
        return this.map.subscribe('goto_saved_location', function() {
          return _this.goToSavedLocation();
        });
      };

      SaveLocation.prototype.saveLocation = function(center, zoom) {
        if (center == null) center = this.map.googleMap.getCenter();
        if (zoom == null) zoom = this.map.getZoom();
        utils.createCookie('lastLocation', center.toUrlValue(), 90);
        return utils.createCookie('lastZoom', zoom, 90);
      };

      SaveLocation.prototype.goToSavedLocation = function() {
        var lastLocation, zoom;
        lastLocation = utils.readCookie('lastLocation');
        zoom = parseInt(utils.readCookie('lastZoom'), 10);
        if (lastLocation && zoom) {
          if (typeof console !== "undefined" && console !== null) {
            console.log('Getting location from cookie...');
          }
          this.map.publish('set_location', lastLocation);
          return this.map.publish('set_zoom', zoom);
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
        return this.map.subscribe('idle', function() {
          return _this.saveLocation();
        });
      };

      return AutosaveLocation;

    })(SaveLocation);
    SaveMapType = (function(_super) {

      __extends(SaveMapType, _super);

      function SaveMapType() {
        SaveMapType.__super__.constructor.apply(this, arguments);
      }

      SaveMapType.prototype.setMap = function(map) {
        var mapTypeId;
        this.map = map;
        this.handleMapEvents();
        mapTypeId = this.getSavedMapType();
        if (__indexOf.call(_.values(googleMaps.MapTypeId), mapTypeId) >= 0) {
          return this.useSavedMapType();
        }
      };

      SaveMapType.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('maptype_loaded', function(mapTypeId) {
          if (mapTypeId === _this.getSavedMapType()) {
            return _this.map.googleMap.setMapTypeId(mapTypeId);
          }
        });
        return this.map.subscribe('initialized', function() {
          return _this.useSavedMapType();
        });
      };

      SaveMapType.prototype.saveMapType = function(mapTypeId) {
        if (mapTypeId == null) mapTypeId = this.map.getMapTypeId();
        return utils.createCookie('mapTypeId', mapTypeId, googleMaps.MapTypeId.ROADMAP);
      };

      SaveMapType.prototype.getSavedMapType = function() {
        return utils.readCookie('mapTypeId' || googleMaps.MapTypeId.ROADMAP);
      };

      SaveMapType.prototype.useSavedMapType = function() {
        var mapTypeId;
        mapTypeId = this.getSavedMapType();
        if (typeof console !== "undefined" && console !== null) {
          console.log('Getting map type from cookie...');
        }
        return this.map.googleMap.setMapTypeId(mapTypeId);
      };

      return SaveMapType;

    })(Component);
    AutosaveMapType = (function(_super) {

      __extends(AutosaveMapType, _super);

      function AutosaveMapType() {
        AutosaveMapType.__super__.constructor.apply(this, arguments);
      }

      AutosaveMapType.prototype.handleMapEvents = function() {
        var _this = this;
        AutosaveMapType.__super__.handleMapEvents.call(this);
        return this.map.subscribe('maptypeid_changed', function() {
          return _this.saveMapType();
        });
      };

      return AutosaveMapType;

    })(SaveMapType);
    StreetView = (function(_super) {

      __extends(StreetView, _super);

      function StreetView() {
        StreetView.__super__.constructor.apply(this, arguments);
      }

      StreetView.prototype.enabled = true;

      StreetView.prototype.init = function() {
        if (typeof console !== "undefined" && console !== null) {
          console.log("Initializing StreetView support.");
        }
        this.streetViewPanel = $("<div>").addClass("map-panel");
        this.streetViewPanel.height("100%").width("50%");
        this.streetViewPanel.hide();
        return this.createObject();
      };

      StreetView.prototype.setMap = function(map) {
        this.map = map;
        this.map.googleMap.controls[googleMaps.ControlPosition.TOP_LEFT].push(this.streetViewPanel.get(0));
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
        this.streetView = new googleMaps.StreetViewPanorama(this.streetViewPanel.get(0), options);
        if ((_ref = this.map) != null) {
          _ref.googleMap.setStreetView(this.streetView);
        }
        return googleMaps.event.addListener(this.streetView, "visible_changed", function() {
          if (_this.streetView.getVisible()) {
            _this.streetViewPanel.show();
          } else {
            _this.streetViewPanel.hide();
          }
          return _this.map.refresh();
        });
      };

      return StreetView;

    })(Component);
    FeatureFilter = (function(_super) {

      __extends(FeatureFilter, _super);

      function FeatureFilter() {
        FeatureFilter.__super__.constructor.apply(this, arguments);
      }

      FeatureFilter.prototype.hooks = {
        'before_feature_setVisible': 'beforeFeatureSetVisibleHook'
      };

      FeatureFilter.prototype.beforeFeatureSetVisibleHook = function(feature, visible) {
        return [feature, visible];
      };

      return FeatureFilter;

    })(Component);
    FeatureZoomFilter = (function(_super) {

      __extends(FeatureZoomFilter, _super);

      function FeatureZoomFilter() {
        FeatureZoomFilter.__super__.constructor.apply(this, arguments);
      }

      FeatureZoomFilter.prototype.hooks = {
        'before_feature_setVisible': 'beforeFeatureSetVisibleHook'
      };

      FeatureZoomFilter.prototype.beforeFeatureSetVisibleHook = function(feature, visible) {
        var zoom;
        zoom = this.map.getZoom();
        visible = visible && ((feature.featureType.minZoomPoint <= zoom && feature.featureType.maxZoomPoint >= zoom) || (feature.featureType.minZoomGeometry <= zoom && feature.featureType.maxZoomGeometry >= zoom));
        return [feature, visible];
      };

      return FeatureZoomFilter;

    })(FeatureFilter);
    window.komoo.controls = {
      DrawingManager: DrawingManager,
      DrawingControl: DrawingControl,
      GeometrySelector: GeometrySelector,
      Balloon: Balloon,
      AjaxBalloon: AjaxBalloon,
      InfoWindow: InfoWindow,
      Tooltip: Tooltip,
      FeatureClusterer: FeatureClusterer,
      CloseBox: CloseBox,
      LoadingBox: LoadingBox,
      SupporterBox: SupporterBox,
      LicenseBox: LicenseBox,
      SearchBox: SearchBox,
      PerimeterSelector: PerimeterSelector,
      Location: Location,
      SaveLocation: SaveLocation,
      AutosaveLocation: AutosaveLocation,
      SaveMapType: SaveMapType,
      AutosaveMapType: AutosaveMapType,
      StreetView: StreetView,
      FeatureFilter: FeatureFilter,
      FeatureZoomFilter: FeatureZoomFilter
    };
    return window.komoo.controls;
  });

}).call(this);
