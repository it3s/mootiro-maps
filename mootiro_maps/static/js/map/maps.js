var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = Object.prototype.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
  __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(function(require) {
  'use strict';
  var AjaxEditor, AjaxMap, Editor, Map, Preview, StaticMap, UserEditor, collections, core, features, geometries, googleMaps, layers, _, _base;
  googleMaps = require('googlemaps');
  _ = require('underscore');
  core = require('./core');
  collections = require('./collections');
  features = require('./features');
  layers = require('./layers');
  geometries = require('./geometries');
  require('./controls');
  require('./maptypes');
  require('./providers');
  if (window.komoo == null) window.komoo = {};
  if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
  Map = (function(_super) {

    __extends(Map, _super);

    Map.prototype.featureTypesUrl = '/map_info/feature_types/';

    Map.prototype.layersUrl = '/map_info/layers/';

    Map.prototype.googleMapDefaultOptions = {
      zoom: 12,
      center: new googleMaps.LatLng(-23.55, -46.65),
      disableDefaultUI: false,
      streetViewControl: true,
      scaleControl: true,
      panControlOptions: {
        position: googleMaps.ControlPosition.RIGHT_TOP
      },
      zoomControlOptions: {
        position: googleMaps.ControlPosition.RIGHT_TOP
      },
      scaleControlOptions: {
        position: googleMaps.ControlPosition.RIGHT_BOTTOM,
        style: googleMaps.ScaleControlStyle.DEFAULT
      },
      mapTypeControlOptions: {
        mapTypeIds: [googleMaps.MapTypeId.ROADMAP, googleMaps.MapTypeId.HYBRID]
      },
      mapTypeId: googleMaps.MapTypeId.HYBRID
    };

    function Map(options) {
      var _ref;
      this.options = options != null ? options : {};
      this.addFeature = __bind(this.addFeature, this);
      Map.__super__.constructor.call(this);
      this.element = (_ref = this.options.element) != null ? _ref : document.getElementById(this.options.elementId);
      this.features = collections.makeFeatureCollectionPlus({
        map: this
      });
      this.components = {};
      this.setProjectId(this.options.projectId);
      this.initGoogleMap(this.options.googleMapOptions);
      this.initFeatureTypes();
      this.initLayers();
      this.handleEvents();
      this.addComponents([
        'map/controls::Location', [
          'map/controls::LayersBox', 'panel', {
            el: '#map-panel-layers'
          }
        ]
      ]);
    }

    Map.prototype.addControl = function(pos, el) {
      return this.googleMap.controls[pos].push(el);
    };

    Map.prototype.loadGeoJsonFromOptions = function() {
      var bounds, features_;
      if (this.options.geojson) {
        features_ = this.loadGeoJSON(this.options.geojson, !(this.options.zoom != null));
        bounds = features_.getBounds();
        if (bounds != null) this.fitBounds(bounds);
        if (features_ != null) {
          features_.setMap(this, {
            geometry: true,
            icon: true
          });
        }
        return this.publish('set_zoom', this.options.zoom);
      }
    };

    Map.prototype.initGoogleMap = function(options) {
      if (options == null) options = this.googleMapDefaultOptions;
      this.googleMap = new googleMaps.Map(this.element, options);
      this.handleGoogleMapEvents();
      return $(this.element).trigger('initialized', this);
    };

    Map.prototype.handleGoogleMapEvents = function() {
      var eventNames,
        _this = this;
      eventNames = ['click', 'idle', 'maptypeid_changed', 'zoom_changed'];
      return eventNames.forEach(function(eventName) {
        return komoo.event.addListener(_this.googleMap, eventName, function(e) {
          return _this.publish(eventName, e);
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
        return this.loadGeoJsonFromOptions();
      } else {
        return $.ajax({
          url: this.featureTypesUrl,
          dataType: 'json',
          success: function(data) {
            data.forEach(function(type) {
              return _this.featureTypes[type.type] = type;
            });
            return _this.loadGeoJsonFromOptions();
          }
        });
      }
    };

    Map.prototype.initLayers = function() {
      if (this.layers == null) this.layers = new layers.Layers;
      if (this.options.layers != null) {
        return this.loadLayersFromOptions(this.options);
      } else {
        return this.loadRemoteLayers(this.layersUrl);
      }
    };

    Map.prototype.loadLayer = function(data) {
      var layer;
      layer = new layers.Layer(_.extend({
        collection: this.getFeatures(),
        map: this
      }, data));
      this.layers.addLayer(layer);
      return this.publish('layer_loaded', layer);
    };

    Map.prototype.loadLayersFromOptions = function(options) {
      var _this = this;
      return options.layers.forEach(function(l) {
        return _this.loadLayer(l);
      });
    };

    Map.prototype.loadRemoteLayers = function(url) {
      var _this = this;
      return $.ajax({
        url: url,
        dataType: 'json',
        success: function(data) {
          return data.forEach(function(l) {
            return _this.loadLayer(l);
          });
        }
      });
    };

    Map.prototype.getLayers = function() {
      return this.layers;
    };

    Map.prototype.getLayer = function(name) {
      return this.layers.getLayer(name);
    };

    Map.prototype.showLayer = function(layer) {
      if (_.isString(layer)) layer = this.getLayer(layer);
      layer.show();
      return this.publish('show_layer', layer);
    };

    Map.prototype.hideLayer = function(layer) {
      if (_.isString(layer)) layer = this.getLayer(layer);
      layer.hide();
      return this.publish('hide_layer', layer);
    };

    Map.prototype.handleEvents = function() {
      var _this = this;
      this.subscribe('features_loaded', function(features_) {
        return komoo.event.trigger(_this, 'features_loaded', features_);
      });
      this.subscribe('close_clicked', function() {
        return komoo.event.trigger(_this, 'close_click');
      });
      this.subscribe('drawing_started', function(feature) {
        return komoo.event.trigger(_this, 'drawing_started', feature);
      });
      this.subscribe('drawing_finished', function(feature, status) {
        komoo.event.trigger(_this, 'drawing_finished', feature, status);
        if (status === false) {
          return _this.revertFeature(feature);
        } else if (!(feature.getProperty("id") != null)) {
          return _this.addFeature(feature);
        }
      });
      this.subscribe('set_location', function(location) {
        var center;
        location = location.split(',');
        center = new googleMaps.LatLng(location[0], location[1]);
        return _this.googleMap.setCenter(center);
      });
      this.subscribe('set_zoom', function(zoom) {
        return _this.setZoom(zoom);
      });
      return this.subscribe('idle', function(zoom) {
        return _this.getFeatures().setVisible(true);
      });
    };

    Map.prototype.addComponent = function(component, type, opts) {
      var component_,
        _this = this;
      if (type == null) type = 'generic';
      if (opts == null) opts = {};
      component_ = _.isString(component) ? this.start(component, opts.el, opts) : this.start(component);
      return this.data.when(component_).done(function() {
        var instance, _base2, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = arguments.length; _i < _len; _i++) {
          instance = arguments[_i];
          instance.setMap(_this);
          if ((_base2 = _this.components)[type] == null) _base2[type] = [];
          _this.components[type].push(instance);
          _results.push(typeof instance.enable === "function" ? instance.enable() : void 0);
        }
        return _results;
      });
    };

    Map.prototype.addComponents = function(components) {
      var component, components_, opts, _i, _len, _ref, _ref2,
        _this = this;
      components_ = [];
      for (_i = 0, _len = components.length; _i < _len; _i++) {
        component = components[_i];
        if (_.isString(component)) component = [component];
        opts = (_ref = component[2]) != null ? _ref : {};
        if (opts.type == null) {
          opts.type = (_ref2 = component[1]) != null ? _ref2 : 'generic';
        }
        components_.push({
          component: component[0],
          el: opts.el,
          opts: opts
        });
      }
      return this.data.when(this.start(components_)).done(function() {
        var instance, _base2, _j, _len2, _name, _results;
        _results = [];
        for (_j = 0, _len2 = arguments.length; _j < _len2; _j++) {
          instance = arguments[_j];
          if (typeof instance.setMap === "function") instance.setMap(_this);
          if ((_base2 = _this.components)[_name = instance.type] == null) {
            _base2[_name] = [];
          }
          _this.components[instance.type].push(instance);
          _results.push(typeof instance.enable === "function" ? instance.enable() : void 0);
        }
        return _results;
      });
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
      return googleMaps.event.trigger(this.googleMap, 'resize');
    };

    Map.prototype.saveLocation = function(center, zoom) {
      if (center == null) center = this.googleMap.getCenter();
      if (zoom == null) zoom = this.getZoom();
      return this.publish('save_location', center, zoom);
    };

    Map.prototype.goToSavedLocation = function() {
      this.publish('goto_saved_location');
      return true;
    };

    Map.prototype.goToUserLocation = function() {
      return this.publish('goto_user_location');
    };

    Map.prototype.handleFeatureEvents = function(feature) {
      var eventsNames,
        _this = this;
      eventsNames = ['mouseover', 'mouseout', 'mousemove', 'click', 'dblclick', 'rightclick', 'highlight_changed'];
      return eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(feature, eventName, function(e) {
          return _this.publish("feature_" + eventName, e, feature);
        });
      });
    };

    Map.prototype.goTo = function(position, displayMarker) {
      if (displayMarker == null) displayMarker = true;
      return this.publish('goto', position, displayMarker);
    };

    Map.prototype.panTo = function(position, displayMarker) {
      if (displayMarker == null) displayMarker = false;
      return this.goTo(position, displayMarker);
    };

    Map.prototype.makeFeature = function(geojson, attach) {
      var feature;
      if (attach == null) attach = true;
      feature = features.makeFeature(geojson, this.featureTypes);
      if (attach) this.addFeature(feature);
      this.publish('feature_created', feature);
      return feature;
    };

    Map.prototype.addFeature = function(feature) {
      this.handleFeatureEvents(feature);
      this.features.push(feature);
      return this.publish('feature_added', feature);
    };

    Map.prototype.revertFeature = function(feature) {
      if (feature.getProperty("id") != null) {} else {
        return feature.setMap(null);
      }
    };

    Map.prototype.getFeatures = function() {
      return this.features;
    };

    Map.prototype.showFeatures = function(features_) {
      if (features_ == null) features_ = this.features;
      return features_.show();
    };

    Map.prototype.hideFeatures = function(features_) {
      if (features_ == null) features_ = this.features;
      return features_.hide();
    };

    Map.prototype.centerFeature = function(type, id) {
      var feature;
      feature = type instanceof features.Feature ? type : this.features.getById(type, id);
      return this.panTo(feature != null ? feature.getCenter() : void 0, false);
    };

    Map.prototype.loadGeoJson = function(geojson, panTo, attach, silent) {
      var features_, _ref,
        _this = this;
      if (panTo == null) panTo = false;
      if (attach == null) attach = true;
      if (silent == null) silent = false;
      features_ = collections.makeFeatureCollection({
        map: this
      });
      if (!((geojson != null ? geojson.type : void 0) != null) || !geojson.type === 'FeatureCollection') {
        return features_;
      }
      if ((_ref = geojson.features) != null) {
        _ref.forEach(function(geojsonFeature) {
          var feature;
          feature = _this.features.getById(geojsonFeature.properties.type, geojsonFeature.properties.id);
          if (feature == null) feature = _this.makeFeature(geojsonFeature, attach);
          features_.push(feature);
          return feature.setVisible(true);
        });
      }
      if (panTo && (features_.getBounds() != null)) this.fitBounds();
      if (!silent) this.publish('features_loaded', features_);
      return features_;
    };

    Map.prototype.loadGeoJSON = function(geojson, panTo, attach, silent) {
      return this.loadGeoJson(geojson, panTo, attach, silent);
    };

    Map.prototype.getGeoJson = function(options) {
      var list;
      if (options == null) options = {};
      if (options.newOnly == null) options.newOnly = false;
      if (options.currentOnly == null) options.currentOnly = false;
      if (options.geometryCollection == null) options.geometryCollection = false;
      list = options.newOnly ? this.newFeatures : options.currentOnly ? collections.makeFeatureCollection({
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
      return this.publish('draw_feature', geometryType, feature);
    };

    Map.prototype.editFeature = function(feature, newGeometry) {
      if (feature == null) feature = this.features.getAt(0);
      if ((newGeometry != null) && feature.getGeometryType() === geometries.types.EMPTY) {
        feature.setGeometry(geometries.makeGeometry({
          geometry: {
            type: newGeometry
          }
        }));
        return this.publish('draw_feature', newGeometry, feature);
      } else {
        return this.publish('edit_feature', feature);
      }
    };

    Map.prototype.setMode = function(mode) {
      this.mode = mode;
      return this.publish('mode_changed', this.mode);
    };

    Map.prototype.selectCenter = function(radius, callback) {
      return this.selectPerimeter(radius, callback);
    };

    Map.prototype.selectPerimeter = function(radius, callback) {
      return this.publish('select_perimeter', radius, callback);
    };

    Map.prototype.highlightFeature = function() {
      this.centerFeature.apply(this, arguments);
      return this.features.highlightFeature.apply(this.features, arguments);
    };

    Map.prototype.getBounds = function() {
      return this.googleMap.getBounds();
    };

    Map.prototype.getZoom = function() {
      return this.googleMap.getZoom();
    };

    Map.prototype.setZoom = function(zoom) {
      if (zoom != null) return this.googleMap.setZoom(zoom);
    };

    Map.prototype.fitBounds = function(bounds) {
      if (bounds == null) bounds = this.features.getBounds();
      return this.googleMap.fitBounds(bounds);
    };

    Map.prototype.getMapTypeId = function() {
      return this.googleMap.getMapTypeId();
    };

    Map.prototype.getProjectId = function() {
      return this.projectId;
    };

    Map.prototype.setProjectId = function(projectId) {
      this.projectId = projectId;
    };

    return Map;

  })(core.Mediator);
  UserEditor = (function(_super) {

    __extends(UserEditor, _super);

    UserEditor.prototype.type = 'editor';

    function UserEditor(options) {
      UserEditor.__super__.constructor.call(this, options);
      this.addComponents(['map/controls::AutosaveMapType', ['map/maptypes::CleanMapType', 'mapType'], ['map/controls::DrawingManager', 'drawing'], 'map/controls::SearchBox']);
    }

    return UserEditor;

  })(Map);
  Editor = (function(_super) {

    __extends(Editor, _super);

    Editor.prototype.type = 'view';

    function Editor(options) {
      Editor.__super__.constructor.call(this, options);
      this.addComponents(['map/controls::AutosaveMapType', 'map/maptypes::CleanMapType', 'map/controls::SaveLocation', 'map/controls::StreetView', 'map/controls::DrawingManager', 'map/controls::DrawingControl', 'map/controls::GeometrySelector', 'map/controls::PerimeterSelector', 'map/controls::SearchBox']);
    }

    return Editor;

  })(Map);
  Preview = (function(_super) {

    __extends(Preview, _super);

    function Preview() {
      Preview.__super__.constructor.apply(this, arguments);
    }

    Preview.prototype.type = 'preview';

    Preview.prototype.googleMapDefaultOptions = {
      zoom: 12,
      center: new googleMaps.LatLng(-23.55, -46.65),
      disableDefaultUI: true,
      streetViewControl: false,
      scaleControl: true,
      scaleControlOptions: {
        position: googleMaps.ControlPosition.RIGHT_BOTTOM,
        style: googleMaps.ScaleControlStyle.DEFAULT
      },
      mapTypeId: googleMaps.MapTypeId.HYBRID
    };

    return Preview;

  })(Map);
  StaticMap = (function(_super) {

    __extends(StaticMap, _super);

    StaticMap.prototype.type = 'view';

    function StaticMap(options) {
      StaticMap.__super__.constructor.call(this, options);
      this.addComponents(['map/controls::AutosaveMapType', ['map/maptypes::CleanMapType', 'mapType'], 'map/controls::AutosaveLocation', 'map/controls::StreetView', ['map/controls::Tooltip', 'tooltip'], ['map/controls::InfoWindow', 'infoWindow'], 'map/controls::LicenseBox', 'map/controls::SearchBox']);
    }

    return StaticMap;

  })(Map);
  AjaxMap = (function(_super) {

    __extends(AjaxMap, _super);

    AjaxMap.prototype.type = 'view';

    function AjaxMap(options) {
      AjaxMap.__super__.constructor.call(this, options);
      this.addComponents([
        'map/controls::LoadingBox', ['map/providers::ZoomFilteredFeatureProvider', 'provider'], [
          'map/controls::CommunityClusterer', 'clusterer', {
            map: this
          }
        ], 'map/controls::FeatureZoomFilter', 'map/controls::LayersFilter'
      ]);
    }

    return AjaxMap;

  })(StaticMap);
  AjaxEditor = (function(_super) {

    __extends(AjaxEditor, _super);

    AjaxEditor.prototype.type = 'editor';

    function AjaxEditor(options) {
      AjaxEditor.__super__.constructor.call(this, options);
      this.addComponents(['map/controls::DrawingManager', 'map/controls::DrawingControl', 'map/controls::GeometrySelector', 'map/controls::PerimeterSelector']);
      if (!this.goToSavedLocation()) this.goToUserLocation();
    }

    return AjaxEditor;

  })(AjaxMap);
  window.komoo.maps = {
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
      } else if (type === 'preview' || type === 'tooltip') {
        return new Preview(options);
      } else if (type === 'userEditor') {
        return new UserEditor(options);
      }
    }
  };
  return window.komoo.maps;
});
