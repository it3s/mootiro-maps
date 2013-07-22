
define(function(require) {
  'use strict';
  var Feature, defaultFeatureType, geometries, googleMaps, _base;
  googleMaps = require('googlemaps');
  geometries = require('./geometries');
  if (window.komoo == null) window.komoo = {};
  if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
  defaultFeatureType = {
    minZoomPoint: 0,
    maxZoomPoint: 10,
    minZoomIcon: 10,
    maxZoomIcon: 100,
    minZoomGeometry: 0,
    maxZoomGeometry: 100
  };
  Feature = (function() {

    Feature.prototype.displayTooltip = true;

    Feature.prototype.displayInfoWindow = true;

    function Feature(options) {
      var geometry;
      this.options = options != null ? options : {};
      geometry = this.options.geometry;
      this.setFeatureType(this.options.featureType);
      if (this.options.geojson) {
        if (this.options.geojson.properties) {
          this.setProperties(this.options.geojson.properties);
        }
        if (geometry == null) {
          geometry = geometries.makeGeometry(this.options.geojson, this);
        }
      }
      if (geometry != null) {
        this.setGeometry(geometry);
        this.createMarker();
      }
    }

    Feature.prototype.createMarker = function() {
      var marker, _ref;
      if ((_ref = this.geometry.getGeometryType()) === 'Point' || _ref === 'MultiPoint') {
        return;
      }
      marker = new geometries.Point({
        visible: false,
        clickable: true
      });
      marker.setCoordinates(this.getCenter());
      return this.setMarker(marker);
    };

    Feature.prototype.initEvents = function(object) {
      var eventsNames, that;
      if (object == null) object = this.geometry;
      that = this;
      eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove', 'mouseout', 'mouseover', 'mouseup', 'rightclick', 'drag', 'dragend', 'draggable_changed', 'dragstart', 'coordinates_changed'];
      return eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(object, eventName, function(e, args) {
          return komoo.event.trigger(that, eventName, e, args);
        });
      });
    };

    Feature.prototype.getGeometry = function() {
      return this.geometry;
    };

    Feature.prototype.setGeometry = function(geometry) {
      this.geometry = geometry;
      this.geometry.feature = this;
      return this.initEvents();
    };

    Feature.prototype.getGeometryType = function() {
      return this.geometry.getGeometryType();
    };

    Feature.prototype.getFeatureType = function() {
      return this.featureType;
    };

    Feature.prototype.setFeatureType = function(featureType) {
      this.featureType = featureType != null ? featureType : defaultFeatureType;
    };

    Feature.prototype.getMarker = function() {
      return this.marker;
    };

    Feature.prototype.setMarker = function(marker) {
      this.marker = marker;
      this.marker.getOverlay().feature = this;
      this.initEvents(this.marker);
      this.marker.setVisible(this.markerShouldBeVisible());
      return this.marker;
    };

    Feature.prototype.handleGeometryEvents = function() {
      var _this = this;
      return komoo.event.addListener(this.geometry, 'coordinates_changed', function(args) {
        _this.updateIcon();
        return komoo.event.trigger(_this, 'coordinates_changed', args);
      });
    };

    Feature.prototype.getUrl = function() {
      var viewName;
      viewName = "view_" + (this.properties.type.toLowerCase());
      return dutils.urls.resolve(viewName, {
        id: this.properties.id
      }).replace('//', '/');
    };

    Feature.prototype.isHighlighted = function() {
      return this.highlighted;
    };

    Feature.prototype.highlight = function() {
      return this.setHighlight(true);
    };

    Feature.prototype.setHighlight = function(highlighted, silent) {
      if (silent == null) silent = false;
      if (this.highlighted === highlighted) return;
      this.highlighted = highlighted;
      this.updateIcon();
      if (!silent) {
        return komoo.event.trigger(this, 'highlight_changed', this.highlighted);
      }
    };

    Feature.prototype.isNew = function() {
      return !this.getProperty('id');
    };

    Feature.prototype.getIconUrl = function(zoom) {
      var categoryOrType, highlighted, nearOrFar, url;
      if (this.getProperty('image')) return this.getProperty('image');
      if (zoom == null) zoom = this.map ? this.map.getZoom() : 10;
      nearOrFar = zoom >= this.featureType.minZoomIcon ? "near" : "far";
      highlighted = this.isHighlighted() ? "highlighted/" : "";
      categoryOrType = this.properties.type.toLowerCase();
      url = ("/static/img/" + nearOrFar + "/" + highlighted + categoryOrType + ".png").replace(' ', '-');
      return url;
    };

    Feature.prototype.updateIcon = function(zoom) {
      return this.setIcon(this.getIconUrl(zoom));
    };

    Feature.prototype.getCategoriesIcons = function() {
      var categorie, _i, _len, _ref, _results;
      _ref = this.getCategories();
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        categorie = _ref[_i];
        _results.push("/static/img/need_categories/" + (category.name.toLowerCase()) + ".png");
      }
      return _results;
    };

    Feature.prototype.getProperties = function() {
      return this.properties;
    };

    Feature.prototype.setProperties = function(properties) {
      this.properties = properties;
    };

    Feature.prototype.getProperty = function(name) {
      return this.properties[name];
    };

    Feature.prototype.setProperty = function(name, value) {
      return this.properties[name] = value;
    };

    Feature.prototype.getType = function() {
      return this.getProperty('type');
    };

    Feature.prototype.getCategories = function() {
      var _ref;
      return (_ref = this.getProperty('categories')) != null ? _ref : [];
    };

    Feature.prototype.getGeometryGeoJson = function() {
      return this.geometry.getGeoJson();
    };

    Feature.prototype.getGeometryCollectionGeoJson = function() {
      return {
        type: "GeometryCollection",
        geometries: [this.getGeometryGeoJson()]
      };
    };

    Feature.prototype.getGeoJsonGeometry = function() {
      return this.getGeometryGeoJson();
    };

    Feature.prototype.getGeoJson = function() {
      return {
        type: 'Feature',
        geometry: this.getGeometryGeoJson(),
        properties: this.getProperties()
      };
    };

    Feature.prototype.getGeoJsonFeature = function() {
      return this.getGeoJson();
    };

    Feature.prototype.setEditable = function(editable) {
      this.editable = editable;
      return this.geometry.setEditable(this.editable);
    };

    Feature.prototype.showGeometry = function() {
      return this.geometry.setMap(this.map);
    };

    Feature.prototype.hideGeometry = function() {
      return this.geometry.setMap(null);
    };

    Feature.prototype.showMarker = function() {
      var _ref;
      if ((_ref = this.marker) != null) _ref.setMap(this.map);
      return this.marker.setVisible(this.markerShouldBeVisible());
    };

    Feature.prototype.hideMarker = function() {
      return this.marker.setVisible(false);
    };

    Feature.prototype.getMap = function() {
      return this.map;
    };

    Feature.prototype.setMap = function(map, force) {
      var _ref;
      if (force == null) {
        force = {
          geometry: false,
          point: false,
          icon: false
        };
      }
      if (map === this.geometry.getMap()) return;
      this.oldMap = this.map;
      if (map != null) this.map = map;
      if ((_ref = this.marker) != null) _ref.setMap(map);
      this.geometry.setMap(map);
      this.updateIcon();
      if (this.oldMap === void 0) return this.handleMapEvents();
    };

    Feature.prototype.handleMapEvents = function() {
      var _this = this;
      return this.map.subscribe('feature_highlight_changed', function(flag, feature) {
        if (feature === _this) return;
        if (_this.isHighlighted()) return _this.setHighlight(false, true);
      });
    };

    Feature.prototype.getBounds = function() {
      return this.geometry.getBounds();
    };

    Feature.prototype.removeFromMap = function() {
      var _ref;
      if ((_ref = this.marker) != null) _ref.setMap(null);
      return this.setMap(null);
    };

    Feature.prototype.markerShouldBeVisible = function() {
      var _ref, _ref2, _ref3, _ref4, _ref5;
      return ((_ref = this.map) != null ? _ref.type : void 0) === 'preview' || (this.featureType.minZoomPoint <= (_ref2 = (_ref3 = this.map) != null ? _ref3.getZoom() : void 0) && _ref2 <= this.featureType.maxZoomPoint) || (this.featureType.minZoomIcon <= (_ref4 = (_ref5 = this.map) != null ? _ref5.getZoom() : void 0) && _ref4 <= this.featureType.maxZoomIcon);
    };

    Feature.prototype.setVisible = function(visible) {
      var feature, visible_, _ref, _ref2, _ref3;
      if (this.editable) {
        visible_ = true;
        feature = this;
      } else {
        _ref2 = (_ref = this.map) != null ? _ref.triggerHooks('before_feature_setVisible', this, visible) : void 0, feature = _ref2[0], visible_ = _ref2[1];
      }
      this.visible = visible_;
      if ((_ref3 = this.marker) != null) {
        _ref3.setVisible(visible_ && this.markerShouldBeVisible());
      }
      return this.geometry.setVisible(visible_);
    };

    Feature.prototype.getCenter = function() {
      return this.geometry.getCenter();
    };

    Feature.prototype.setOptions = function(options) {
      return this.geometry.setOptions(options);
    };

    Feature.prototype.getIcon = function() {
      return this.geometry.getIcon();
    };

    Feature.prototype.setIcon = function(icon) {
      var _ref;
      if ((_ref = this.marker) != null) _ref.setIcon(icon);
      return this.geometry.setIcon(icon);
    };

    Feature.prototype.getBorderSize = function() {
      return this.featureType.border_size;
    };

    Feature.prototype.getBorderSizeHover = function() {
      return this.featureType.borderSizeHover;
    };

    Feature.prototype.getBorderColor = function() {
      return this.featureType.borderColor;
    };

    Feature.prototype.getBorderOpacity = function() {
      return this.featureType.borderOpacity;
    };

    Feature.prototype.getBackgroundColor = function() {
      return this.featureType.backgroundColor;
    };

    Feature.prototype.getBackgroundOpacity = function() {
      return this.featureType.backgroundOpacity;
    };

    Feature.prototype.getDefaultZIndex = function() {
      return this.featureType.zIndex;
    };

    return Feature;

  })();
  window.komoo.features = {
    Feature: Feature,
    makeFeature: function(geojson, featureTypes) {
      var _ref;
      return new komoo.features.Feature({
        geojson: geojson,
        featureType: featureTypes != null ? featureTypes[geojson != null ? (_ref = geojson.properties) != null ? _ref.type : void 0 : void 0] : void 0
      });
    }
  };
  return window.komoo.features;
});
