(function() {
  var Feature, _base;

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

  Feature = (function() {

    function Feature(options) {
      var geometry, marker;
      this.options = options != null ? options : {};
      geometry = this.options.geometry;
      if (this.options.geojson) {
        if (this.options.geojson.properties) {
          this.setProperties(this.options.geojson.properties);
        }
        if (geometry == null) {
          geometry = komoo.geometries.makeGeometry(this.options.geojson);
        }
      }
      if (geometry != null) {
        this.setGeometry(geometry);
        marker = new komoo.geometries.Point({
          visible: true,
          clickable: true
        });
        marker.setCoordinates(this.getCenter());
        this.setMarker(marker);
      }
    }

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
      return this.initEvents();
    };

    Feature.prototype.getGeometryType = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.getGeometryType() : void 0;
    };

    Feature.prototype.getMarker = function() {
      return this.marker;
    };

    Feature.prototype.setMarker = function(marker) {
      this.marker = marker;
      this.marker.getOverlay().feature = this;
      this.initEvents(this.marker);
      return this.marker;
    };

    Feature.prototype.handleGeometryEvents = function() {
      var that;
      that = this;
      return komoo.event.addListener(this.geometry, 'coordinates_changed', function(args) {
        this.updateIcon();
        return komoo.event.trigger(that, 'coordinates_changed', args);
      });
    };

    Feature.prototype.getUrl = function() {
      var params, slugname;
      if (this.properties.type === 'Community') {
        return dutils.urls.resolve('view_community', {
          community_slug: this.properties.community_slug
        });
      } else if (this.properties.type === 'Resource') {
        return dutils.url.resolve('view_resource', {
          resource_id: this.properties.id
        }).replace('//', '/');
      } else if (this.properties.type === 'OrganizationBranch') {
        return dutils.url.resolve('view_organization', {
          organization_slug: this.properties.organization_slug
        }).replace('//', '/');
      } else {
        slugname = "" + (this.properties.type.toLowerCase()) + "_slug";
        params = {
          community_slug: this.properties.community_slug
        };
        params[slugname] = this.properties[slugname];
        return dutils.url.resolve("view_" + (this.properties.type.toLowerCase()), params).replace('//', '/');
      }
    };

    Feature.prototype.isHighlighted = function() {
      return this.highlighted != null;
    };

    Feature.prototype.highlight = function() {
      return this.setHighlight(true);
    };

    Feature.prototype.setHighlight = function(highlighted) {
      this.highlighted = highlighted;
      this.updateIcons();
      return komoo.event.trigger(this, 'highlight_changed', this.highlighted);
    };

    Feature.prototype.getIconUrl = function(zoom) {
      var categoryOrType, highlighted, nearOrFar;
      if (zoom == null) zoom = this.map ? this.map.getZoom() : 10;
      nearOrFar = zoom >= this.minZoomMarker ? "near" : "far";
      highlighted = this.isHighlighted() ? "highlighted/" : "";
      categoryOrType = this.properties.categories && zoom >= this.minZoomMarker ? this.properties.categories[0].name.toLowerCase() + (this.properties.categories.length > 1 ? "-plus" : "") : this.properties.type.toLowerCase();
      return "/static/img/" + nearOrFar + "/" + highlighted + categoryOrType + ".png";
    };

    Feature.prototype.updateIcon = function(zoom) {
      return this.setIcon(this.getIconUrl(zoom));
    };

    Feature.prototype.getCategoriesIcons = function() {
      var categorie, _i, _len, _ref, _results;
      _ref = this.properties.categories;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        categorie = _ref[_i];
        _results.push("/static/need_categories/" + (category.name.toLowerCase()) + ".png");
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

    Feature.prototype.getGeoJsonGeometry = function() {
      var _ref, _ref2;
      return {
        type: (_ref = this.geometry) != null ? _ref.getGeometryType() : void 0,
        coordinates: (_ref2 = this.geometry) != null ? _ref2.getCoordinates() : void 0
      };
    };

    Feature.prototype.getGeoJsonFeature = function() {
      return {
        type: 'Feature',
        geometry: this.getGeoJsonGeometry(),
        properties: this.getProperties()
      };
    };

    Feature.prototype.setEditable = function(editable) {
      var _ref;
      this.editable = editable;
      return (_ref = this.geometry) != null ? _ref.setEditable(this.editable) : void 0;
    };

    Feature.prototype.showGeometry = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.setMap(this.map) : void 0;
    };

    Feature.prototype.hideGeometry = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.setMap(null) : void 0;
    };

    Feature.prototype.showMarker = function() {
      var _ref;
      return (_ref = this.marker) != null ? _ref.setMap(this.map) : void 0;
    };

    Feature.prototype.hideMarker = function() {
      var _ref;
      return (_ref = this.marker) != null ? _ref.setMap(this.map) : void 0;
    };

    Feature.prototype.getMap = function() {
      return this.map;
    };

    Feature.prototype.setMap = function(map, force) {
      var zoom, _ref, _ref2;
      this.map = map;
      if (force == null) {
        force = {
          geometry: false,
          marker: false
        };
      }
      if (this.properties.alwaysVisible === true) {
        force = {
          geometry: true,
          marker: false
        };
      }
      zoom = this.map != null ? this.map.getZoom() : 0;
      if ((_ref = this.marker) != null) {
        _ref.setMap((zoom <= this.maxZoomMarker && zoom >= this.minZoomMarker) || force.marker ? this.map : null);
      }
      return (_ref2 = this.geometry) != null ? _ref2.setMap((zoom <= this.maxZoomGeometry && zoom >= this.minZoomGeometry) || force.geometry ? this.map : null) : void 0;
    };

    Feature.prototype.getBounds = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.getBounds() : void 0;
    };

    Feature.prototype.removeFromMap = function() {
      var _ref;
      if ((_ref = this.marker) != null) _ref.setMap(null);
      return this.setMap(null);
    };

    Feature.prototype.setVisible = function(visible) {
      var _ref, _ref2;
      this.visible = visible;
      if ((_ref = this.marker) != null) _ref.setVisible(this.visible);
      return (_ref2 = this.geometry) != null ? _ref2.setVisible(this.visible) : void 0;
    };

    Feature.prototype.getCenter = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.getCenter() : void 0;
    };

    Feature.prototype.setOptions = function(options) {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.setOptions(options) : void 0;
    };

    Feature.prototype.getIcon = function() {
      var _ref;
      return (_ref = this.geometry) != null ? _ref.getIcon() : void 0;
    };

    Feature.prototype.setIcon = function(icon) {
      var _ref, _ref2;
      if ((_ref = this.marker) != null) _ref.setIcon(icon);
      return (_ref2 = this.geometry) != null ? _ref2.setIcon(icon) : void 0;
    };

    return Feature;

  })();

  window.komoo.features = {
    Feature: Feature,
    makeFeature: function(geojson) {
      return new komoo.features.Feature({
        geojson: geojson
      });
    }
  };

}).call(this);
