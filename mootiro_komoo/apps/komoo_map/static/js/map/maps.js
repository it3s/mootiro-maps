(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(['map/controls', 'map/maptypes', 'map/providers', 'map/collections', 'map/features'], function() {
    var AjaxEditor, AjaxMap, Editor, Map, Preview, StaticMap, UserEditor, _base;
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = google.maps.event;
    Map = (function() {

      Map.prototype.featureTypesUrl = '/map_info/feature_types/';

      Map.prototype.googleMapDefaultOptions = {
        zoom: 12,
        center: new google.maps.LatLng(-23.55, -46.65),
        disableDefaultUI: false,
        streetViewControl: true,
        scaleControl: true,
        panControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP
        },
        zoomControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP
        },
        scaleControlOptions: {
          position: google.maps.ControlPosition.RIGHT_BOTTOM,
          style: google.maps.ScaleControlStyle.DEFAULT
        },
        mapTypeControlOptions: {
          mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.HYBRID]
        },
        mapTypeId: google.maps.MapTypeId.HYBRID
      };

      function Map(options) {
        var _ref;
        this.options = options != null ? options : {};
        this.addFeature = __bind(this.addFeature, this);
        this.element = (_ref = this.options.element) != null ? _ref : document.getElementById(this.options.elementId);
        this.features = komoo.collections.makeFeatureCollectionPlus({
          map: this
        });
        this.components = {};
        this.addComponent(komoo.controls.makeLocation());
        this.initGoogleMap(this.options.googleMapOptions);
        this.initFeatureTypes();
        this.handleEvents();
      }

      Map.prototype.loadGeoJsonFromOptons = function() {
        var bounds, features;
        if (this.options.geojson) {
          features = this.loadGeoJSON(this.options.geojson, !(this.options.zoom != null));
          bounds = features.getBounds();
          if (bounds != null) this.fitBounds(bounds);
          if (features != null) {
            features.setMap(this, {
              geometry: true,
              icon: true
            });
          }
          return this.setZoom(this.options.zoom);
        }
      };

      Map.prototype.initGoogleMap = function(options) {
        if (options == null) options = this.googleMapDefaultOptions;
        this.googleMap = new google.maps.Map(this.element, options);
        this.handleGoogleMapEvents();
        return $(this.element).trigger('initialized', this);
      };

      Map.prototype.handleGoogleMapEvents = function() {
        var eventNames,
          _this = this;
        eventNames = ['click', 'idle'];
        return eventNames.forEach(function(eventName) {
          return komoo.event.addListener(_this.googleMap, eventName, function(e) {
            return komoo.event.trigger(_this, eventName, e);
          });
        });
      };

      Map.prototype.initFeatureTypes = function() {
        var _ref,
          _this = this;
        if (this.featureTypes == null) this.featureTypes = {};
        if (this.options.featureTypes != null) {
          if ((_ref = this.options.featureTypes) != null) {
            _ref.forEach(function(type) {
              return _this.featureTypes[type.type] = type;
            });
          }
          return this.loadGeoJsonFromOptons();
        } else {
          return $.ajax({
            url: this.featureTypesUrl,
            dataType: 'json',
            success: function(data) {
              data.forEach(function(type) {
                return _this.featureTypes[type.type] = type;
              });
              return _this.loadGeoJsonFromOptons();
            }
          });
        }
      };

      Map.prototype.handleEvents = function() {
        var _this = this;
        return komoo.event.addListener(this, "drawing_finished", function(feature, status) {
          if (status === false) {
            return _this.revertFeature(feature);
          } else if (!(feature.getProperty("id") != null)) {
            return _this.addFeature(feature);
          }
        });
      };

      Map.prototype.addComponent = function(component, type) {
        var _base2;
        if (type == null) type = 'generic';
        component.setMap(this);
        if ((_base2 = this.components)[type] == null) _base2[type] = [];
        this.components[type].push(component);
        return typeof component.enable === "function" ? component.enable() : void 0;
      };

      Map.prototype.enableComponents = function(type) {
        var _ref,
          _this = this;
        return (_ref = this.components[type]) != null ? _ref.forEach(function(component) {
          return typeof component.enable === "function" ? component.enable() : void 0;
        }) : void 0;
      };

      Map.prototype.disableComponents = function(type) {
        var _ref,
          _this = this;
        return (_ref = this.components[type]) != null ? _ref.forEach(function(component) {
          return typeof component.disable === "function" ? component.disable() : void 0;
        }) : void 0;
      };

      Map.prototype.getComponentsStatus = function(type) {
        var status, _ref,
          _this = this;
        status = [];
        if ((_ref = this.components[type]) != null) {
          _ref.forEach(function(component) {
            if (component.enabled === true) return status.push('enabled');
          });
        }
        if (__indexOf.call(status, 'enabled') >= 0) {
          return 'enabled';
        } else {
          return 'disabled';
        }
      };

      Map.prototype.clear = function() {
        this.features.removeAllFromMap();
        return this.features.clear();
      };

      Map.prototype.refresh = function() {
        return google.maps.event.trigger(this.googleMap, 'resize');
      };

      Map.prototype.saveLocation = function(center, zoom) {
        if (center == null) center = this.googleMap.getCenter();
        if (zoom == null) zoom = this.getZoom();
        return komoo.event.trigger(this, 'save_location', center, zoom);
      };

      Map.prototype.goToSavedLocation = function() {
        komoo.event.trigger(this, 'goto_saved_location');
        return true;
      };

      Map.prototype.goToUserLocation = function() {
        return komoo.event.trigger(this, 'goto_user_location');
      };

      Map.prototype.handleFeatureEvents = function(feature) {
        var eventsNames,
          _this = this;
        eventsNames = ['mouseover', 'mouseout', 'mousemove', 'click', 'dblclick', 'rightclick', 'highlight_changed'];
        return eventsNames.forEach(function(eventName) {
          return komoo.event.addListener(feature, eventName, function(e) {
            return komoo.event.trigger(_this, "feature_" + eventName, e, feature);
          });
        });
      };

      Map.prototype.goTo = function(position, displayMarker) {
        if (displayMarker == null) displayMarker = true;
        return komoo.event.trigger(this, 'goto', position, displayMarker);
      };

      Map.prototype.panTo = function(position, displayMarker) {
        if (displayMarker == null) displayMarker = false;
        return this.goTo(position, displayMarker);
      };

      Map.prototype.makeFeature = function(geojson, attach) {
        var feature;
        if (attach == null) attach = true;
        feature = komoo.features.makeFeature(geojson, this.featureTypes);
        if (attach) this.addFeature(feature);
        komoo.event.trigger(this, 'feature_created', feature);
        return feature;
      };

      Map.prototype.addFeature = function(feature) {
        this.handleFeatureEvents(feature);
        return this.features.push(feature);
      };

      Map.prototype.revertFeature = function(feature) {
        if (feature.getProperty("id") != null) {} else {
          return feature.setMap(null);
        }
      };

      Map.prototype.getFeatures = function() {
        return this.features;
      };

      Map.prototype.getFeaturesByType = function(type, categories, strict) {
        return this.features.getByType(type, categories, strict);
      };

      Map.prototype.showFeaturesByType = function(type, categories, strict) {
        var _ref;
        return (_ref = this.getFeaturesByType(type, categories, strict)) != null ? _ref.show() : void 0;
      };

      Map.prototype.hideFeaturesByType = function(type, categories, strict) {
        var _ref;
        return (_ref = this.getFeaturesByType(type, categories, strict)) != null ? _ref.hide() : void 0;
      };

      Map.prototype.showFeatures = function(features) {
        if (features == null) features = this.features;
        return features.show();
      };

      Map.prototype.hideFeatures = function(features) {
        if (features == null) features = this.features;
        return features.hide();
      };

      Map.prototype.centerFeature = function(type, id) {
        var feature;
        feature = type instanceof komoo.features.Feature ? type : this.features.getById(type, id);
        return this.panTo(feature != null ? feature.getCenter() : void 0, false);
      };

      Map.prototype.loadGeoJson = function(geojson, panTo, attach) {
        var features, _ref, _ref2,
          _this = this;
        if (panTo == null) panTo = false;
        if (attach == null) attach = true;
        features = komoo.collections.makeFeatureCollection({
          map: this
        });
        if (!((geojson != null ? geojson.type : void 0) != null) || !geojson.type === 'FeatureCollection') {
          return features;
        }
        if ((_ref = geojson.features) != null) {
          _ref.forEach(function(geojsonFeature) {
            var feature;
            feature = _this.features.getById(geojsonFeature.properties.type, geojsonFeature.properties.id);
            if (feature == null) {
              feature = _this.makeFeature(geojsonFeature, attach);
            }
            return features.push(feature);
          });
        }
        if (panTo && ((_ref2 = features.getAt(0)) != null ? _ref2.getBounds() : void 0)) {
          this.googleMap.fitBounds(features.getAt(0).getBounds());
        }
        komoo.event.trigger(this, 'features_loaded', features);
        return features;
      };

      Map.prototype.loadGeoJSON = function(geojson, panTo, attach) {
        return this.loadGeoJson(geojson, panTo, attach);
      };

      Map.prototype.getGeoJson = function(options) {
        var list;
        if (options == null) options = {};
        if (options.newOnly == null) options.newOnly = false;
        if (options.currentOnly == null) options.currentOnly = false;
        if (options.geometryCollection == null) options.geometryCollection = false;
        list = options.newOnly ? this.newFeatures : options.currentOnly ? komoo.collections.makeFeatureCollection({
          map: this.map,
          features: [this.currentFeature]
        }) : this.features;
        return list.getGeoJson({
          geometryCollection: options.geometryCollection
        });
      };

      Map.prototype.getGeoJSON = function(options) {
        return this.getGeoJson(options);
      };

      Map.prototype.drawNewFeature = function(geometryType, featureType) {
        var feature;
        feature = this.makeFeature({
          type: 'Feature',
          geometry: {
            type: geometryType
          },
          properties: {
            name: "New " + featureType,
            type: featureType
          }
        });
        return komoo.event.trigger(this, 'draw_feature', geometryType, feature);
      };

      Map.prototype.editFeature = function(feature, newGeometry) {
        if (feature == null) feature = this.features.getAt(0);
        if ((newGeometry != null) && feature.getGeometryType() === komoo.geometries.types.EMPTY) {
          feature.setGeometry(komoo.geometries.makeGeometry({
            geometry: {
              type: newGeometry
            }
          }));
          return komoo.event.trigger(this, 'draw_feature', newGeometry, feature);
        } else {
          return komoo.event.trigger(this, 'edit_feature', feature);
        }
      };

      Map.prototype.setMode = function(mode) {
        this.mode = mode;
        return komoo.event.trigger(this, 'mode_changed', this.mode);
      };

      Map.prototype.selectCenter = function(radius, callback) {
        return this.selectPerimeter(radius, callback);
      };

      Map.prototype.selectPerimeter = function(radius, callback) {
        return komoo.event.trigger(this, 'select_perimeter', radius, callback);
      };

      Map.prototype.highlightFeature = function() {
        this.centerFeature.apply(this, arguments);
        return this.features.highlightFeature.apply(this.features, arguments);
      };

      Map.prototype.getBounds = function() {
        return this.googleMap.getBounds();
      };

      Map.prototype.setZoom = function(zoom) {
        if (zoom != null) return this.googleMap.setZoom(zoom);
      };

      Map.prototype.getZoom = function() {
        return this.googleMap.getZoom();
      };

      Map.prototype.fitBounds = function(bounds) {
        if (bounds == null) bounds = this.features.getBounds();
        return this.googleMap.fitBounds(bounds);
      };

      return Map;

    })();
    UserEditor = (function(_super) {

      __extends(UserEditor, _super);

      function UserEditor(options) {
        UserEditor.__super__.constructor.call(this, options);
        this.addComponent(komoo.maptypes.makeCleanMapType(), 'mapType');
        this.addComponent(komoo.controls.makeDrawingManager(), 'drawing');
      }

      return UserEditor;

    })(Map);
    Editor = (function(_super) {

      __extends(Editor, _super);

      function Editor(options) {
        Editor.__super__.constructor.call(this, options);
        this.addComponent(komoo.maptypes.makeCleanMapType(), 'mapType');
        this.addComponent(komoo.controls.makeSaveLocation());
        this.addComponent(komoo.controls.makeStreetView());
        this.addComponent(komoo.controls.makeDrawingManager(), 'drawing');
        this.addComponent(komoo.controls.makeDrawingControl(), 'drawing');
        this.addComponent(komoo.controls.makeSupporterBox());
        this.addComponent(komoo.controls.makePerimeterSelector(), 'perimeter');
      }

      return Editor;

    })(Map);
    Preview = (function(_super) {

      __extends(Preview, _super);

      function Preview() {
        Preview.__super__.constructor.apply(this, arguments);
      }

      Preview.prototype.googleMapDefaultOptions = {
        zoom: 12,
        center: new google.maps.LatLng(-23.55, -46.65),
        disableDefaultUI: true,
        streetViewControl: false,
        scaleControl: true,
        scaleControlOptions: {
          position: google.maps.ControlPosition.RIGHT_BOTTOM,
          style: google.maps.ScaleControlStyle.DEFAULT
        },
        mapTypeId: google.maps.MapTypeId.HYBRID
      };

      return Preview;

    })(Map);
    StaticMap = (function(_super) {

      __extends(StaticMap, _super);

      function StaticMap(options) {
        StaticMap.__super__.constructor.call(this, options);
        this.addComponent(komoo.maptypes.makeCleanMapType(), 'mapType');
        this.addComponent(komoo.controls.makeAutosaveLocation());
        this.addComponent(komoo.controls.makeStreetView());
        this.addComponent(komoo.controls.makeTooltip(), 'tooltip');
        this.addComponent(komoo.controls.makeInfoWindow(), 'infoWindow');
        this.addComponent(komoo.controls.makeSupporterBox());
        this.addComponent(komoo.controls.makeLicenseBox());
      }

      StaticMap.prototype.loadGeoJson = function(geojson, panTo, attach) {
        var features,
          _this = this;
        if (panTo == null) panTo = false;
        if (attach == null) attach = true;
        features = StaticMap.__super__.loadGeoJson.call(this, geojson, panTo, attach);
        features.forEach(function(feature) {
          return feature.setMap(_this, {
            geometry: true
          });
        });
        return features;
      };

      return StaticMap;

    })(Map);
    AjaxMap = (function(_super) {

      __extends(AjaxMap, _super);

      function AjaxMap(options) {
        AjaxMap.__super__.constructor.call(this, options);
        this.addComponent(komoo.providers.makeFeatureProvider(), 'provider');
      }

      return AjaxMap;

    })(StaticMap);
    AjaxEditor = (function(_super) {

      __extends(AjaxEditor, _super);

      function AjaxEditor(options) {
        AjaxEditor.__super__.constructor.call(this, options);
        this.addComponent(komoo.controls.makeDrawingManager(), 'drawing');
        this.addComponent(komoo.controls.makeDrawingControl(), 'drawing');
        this.addComponent(komoo.controls.makePerimeterSelector(), 'perimeter');
      }

      return AjaxEditor;

    })(AjaxMap);
    return window.komoo.maps = {
      Map: Map,
      Preview: Preview,
      AjaxMap: AjaxMap,
      makeMap: function(options) {
        var type, _ref;
        if (options == null) options = {};
        type = (_ref = options.type) != null ? _ref : 'map';
        if (type === 'main') {
          return new AjaxEditor(options);
        } else if (type === 'editor') {
          return new Editor(options);
        } else if (type === 'view') {
          return new AjaxMap(options);
        } else if (type === 'static') {
          return new StaticMap(options);
        } else if (type === 'preview') {
          return new Preview(options);
        } else if (type === 'userEditor') {
          return new UserEditor(options);
        }
      }
    };
  });

}).call(this);
