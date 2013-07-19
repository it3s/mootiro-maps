(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var FeatureCollection, FeatureCollectionPlus, GenericCollection, Layer, googleMaps, _base;
    googleMaps = require('googlemaps');
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
    GenericCollection = (function() {

      function GenericCollection(options) {
        this.options = options != null ? options : {};
        this.elements = [];
        this.length = 0;
      }

      GenericCollection.prototype.updateLength = function() {
        return this.length = this.elements.length;
      };

      GenericCollection.prototype.clear = function() {
        this.elements = [];
        return this.updateLength();
      };

      GenericCollection.prototype.getAt = function(index) {
        return this.elements[index];
      };

      GenericCollection.prototype.push = function(element) {
        this.elements.push(element);
        return this.updateLength();
      };

      GenericCollection.prototype.pop = function() {
        var element;
        element = this.elements.pop();
        this.updateLength();
        return element;
      };

      GenericCollection.prototype.forEach = function(callback, thisArg) {
        return this.elements.forEach(callback, thisArg);
      };

      GenericCollection.prototype.getArray = function() {
        return this.elements;
      };

      GenericCollection.prototype.slice = function(begin, end) {
        return this.elements.slice(begin, end);
      };

      return GenericCollection;

    })();
    FeatureCollection = (function(_super) {

      __extends(FeatureCollection, _super);

      function FeatureCollection(options) {
        var _ref,
          _this = this;
        if (options == null) options = {};
        FeatureCollection.__super__.constructor.call(this, options);
        if (options.map) this.setMap(options.map);
        if ((_ref = options.features) != null) {
          _ref.forEach(function(feature) {
            return _this.push(feature);
          });
        }
      }

      FeatureCollection.prototype.push = function(feature) {
        if (!(feature != null)) return;
        FeatureCollection.__super__.push.call(this, feature);
        return feature.setMap(this.map);
      };

      FeatureCollection.prototype.getBounds = function() {
        var firstFeature, geometry, point,
          _this = this;
        firstFeature = this.getAt(0);
        if (firstFeature && firstFeature.getGeometryType() !== 'Empty') {
          geometry = firstFeature.getGeometry();
          point = geometry.getLatLngFromArray(geometry.getCenter());
          this.bounds = new googleMaps.LatLngBounds(point, point);
          this.forEach(function(feature) {
            var _ref;
            if (feature.getGeometryType() !== 'Empty') {
              return (_ref = _this.bounds) != null ? _ref.union(feature.getBounds()) : void 0;
            }
          });
        }
        return this.bounds;
      };

      FeatureCollection.prototype.setMap = function(map, force) {
        var tmpForce,
          _this = this;
        this.map = map;
        tmpForce = null;
        this.forEach(function(feature) {
          if (force != null) {
            tmpForce = {
              geometry: force != null ? force.geometry : void 0,
              point: force != null ? force.icon : void 0,
              icon: force != null ? force.icon : void 0
            };
          }
          if (feature.getType() === 'Community') {
            if (tmpForce != null) tmpForce['point'] = false;
          }
          return feature != null ? feature.setMap(_this.map, tmpForce) : void 0;
        });
        return this.handleMapEvents();
      };

      FeatureCollection.prototype.show = function() {
        this.setMap(this.map, {
          geometry: true
        });
        return this.setVisible(true);
      };

      FeatureCollection.prototype.hide = function() {
        return this.setVisible(false);
      };

      FeatureCollection.prototype.getGeoJson = function(options) {
        var geojson;
        if (options.geometryCollection == null) options.geometryCollection = false;
        if (options.geometryCollection) {
          geojson = {
            type: "GeometryCollection",
            geometries: []
          };
          this.forEach(function(feature) {
            return geojson.geometries.push(feature.getGeometryGeoJson());
          });
        } else {
          geojson = {
            type: "FeatureCollection",
            features: []
          };
          this.forEach(function(feature) {
            return geojson.features.push(feature.getGeoJson());
          });
        }
        return geojson;
      };

      FeatureCollection.prototype.removeAllFromMap = function() {
        return this.forEach(function(feature) {
          return feature.removeFromMap();
        });
      };

      FeatureCollection.prototype.setVisible = function(flag) {
        return this.forEach(function(feature) {
          return feature.setVisible(flag);
        });
      };

      FeatureCollection.prototype.updateFeaturesVisibility = function() {
        return this.forEach(function(feature) {
          return feature.seMap(feature.getMap());
        });
      };

      FeatureCollection.prototype.handleMapEvents = function() {
        var _this = this;
        return komoo.event.addListener(this.map, "zoom_changed", function() {});
      };

      return FeatureCollection;

    })(GenericCollection);
    FeatureCollectionPlus = (function(_super) {

      __extends(FeatureCollectionPlus, _super);

      function FeatureCollectionPlus(options) {
        if (options == null) options = {};
        FeatureCollectionPlus.__super__.constructor.call(this, options);
        this.featuresByType = {};
      }

      FeatureCollectionPlus.prototype.push = function(feature) {
        var type, _base2, _base3, _base4, _base5, _base6, _ref,
          _this = this;
        FeatureCollectionPlus.__super__.push.call(this, feature);
        type = feature.getType();
        if ((_base2 = this.featuresByType)[type] == null) _base2[type] = {};
        if ((_base3 = this.featuresByType[type])['categories'] == null) {
          _base3['categories'] = {};
        }
        if ((_base4 = this.featuresByType[type]['categories'])['all'] == null) {
          _base4['all'] = new FeatureCollection({
            map: this.map
          });
        }
        if ((_base5 = this.featuresByType[type]['categories'])['uncategorized'] == null) {
          _base5['uncategorized'] = new FeatureCollection({
            map: this.map
          });
        }
        if ((_ref = feature.getCategories()) != null) {
          _ref.forEach(function(category) {
            var _base6, _name;
            if ((_base6 = _this.featuresByType[type]['categories'])[_name = category.name] == null) {
              _base6[_name] = new FeatureCollection({
                map: _this.map
              });
            }
            return _this.featuresByType[type]['categories'][category.name].push(feature);
          });
        }
        if (!(feature.getCategories() != null) || feature.getCategories().length === 0) {
          this.featuresByType[type]['categories']['uncategorized'].push(feature);
        }
        this.featuresByType[type]['categories']['all'].push(feature);
        if ((_base6 = this.featuresByType[type])['ids'] == null) {
          _base6['ids'] = {};
        }
        return this.featuresByType[type]['ids'][feature.getProperty('id')] = feature;
      };

      FeatureCollectionPlus.prototype.pop = function() {
        return FeatureCollectionPlus.__super__.pop.call(this);
      };

      FeatureCollectionPlus.prototype.clear = function() {
        this.featuresByType = {};
        return FeatureCollectionPlus.__super__.clear.call(this);
      };

      FeatureCollectionPlus.prototype.getByType = function(type, categories, strict) {
        var features,
          _this = this;
        if (strict == null) strict = false;
        if (!this.featuresByType[type]) {
          return false;
        } else if (!categories) {
          return this.featuresByType[type]['categories']['all'];
        } else if (categories.length === 0) {
          return this.featuresByType[type]['categories']['uncategorized'];
        } else {
          features = new FeatureCollection({
            map: this.map
          });
          categories.forEach(function(category) {
            if (_this.featuresByType[type]['categories'][category]) {
              return _this.featuresByType[type]['categories'][category].forEach(function(feature) {
                if (!strict || !feature.getCategories() || feature.getCategories().length === 1) {
                  return features.push(feature);
                }
              });
            }
          });
          return features;
        }
      };

      FeatureCollectionPlus.prototype.getById = function(type, id) {
        var _ref;
        return (_ref = this.featuresByType[type]) != null ? _ref['ids'][id] : void 0;
      };

      FeatureCollectionPlus.prototype.highlightFeature = function(type, id) {
        var feature, _ref;
        feature = typeof type === 'string' ? this.getById(type, id) : type;
        if (feature.isHighlighted()) return;
        if ((_ref = this.highlighted) != null) _ref.setHighlight(false);
        feature.highlight();
        return this.highlighted = feature;
      };

      return FeatureCollectionPlus;

    })(FeatureCollection);
    Layer = (function(_super) {

      __extends(Layer, _super);

      function Layer() {
        Layer.__super__.constructor.apply(this, arguments);
      }

      return Layer;

    })(FeatureCollection);
    window.komoo.collections = {
      GenericCollection: GenericCollection,
      FeatureCollection: FeatureCollection,
      FeatureCollectionPlus: FeatureCollectionPlus,
      makeFeatureCollection: function(options) {
        if (options == null) options = {};
        return new FeatureCollection(options);
      },
      makeFeatureCollectionPlus: function(options) {
        if (options == null) options = {};
        return new FeatureCollectionPlus(options);
      }
    };
    return window.komoo.collections;
  });

}).call(this);
