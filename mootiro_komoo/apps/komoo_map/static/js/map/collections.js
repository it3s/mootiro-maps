(function() {
  var FeatureCollection, FeatureCollectionPlus, GenericCollection, Layer, _base,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

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
      FeatureCollection.__super__.push.call(this, feature);
      return feature.setMap(this.map);
    };

    FeatureCollection.prototype.setMap = function(map, force) {
      var _this = this;
      this.map = map;
      this.forEach(function(feature) {
        return feature.setMap(_this.map, force);
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

    FeatureCollection.prototype.getGeoJson = function() {
      var features, geojson;
      features = [];
      geojson = {
        type: "FeatureCollection",
        features: features
      };
      this.forEach(function(feature) {
        return features.push(feature.getGeoJson());
      });
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
      var _base2, _base3, _base4, _name, _ref,
        _this = this;
      FeatureCollectionPlus.__super__.push.call(this, feature);
      if ((_base2 = this.featuresByType)[_name = feature.getType()] == null) {
        _base2[_name] = {};
      }
      if ((_base3 = this.featuresByType[feature.getType()])['all'] == null) {
        _base3['all'] = new FeatureCollection({
          map: this.map
        });
      }
      if ((_base4 = this.featuresByType[feature.getType()])['uncategorized'] == null) {
        _base4['uncategorized'] = new FeatureCollection({
          map: this.map
        });
      }
      if ((_ref = feature.getCategories()) != null) {
        _ref.forEach(function(category) {
          var _base5, _name2;
          if ((_base5 = _this.featuresByType[feature.getType()])[_name2 = category.name] == null) {
            _base5[_name2] = new FeatureCollection({
              map: _this.map
            });
          }
          return _this.featuresByType[feature.getType()][category.name].push(feature);
        });
      }
      if (!(feature.getCategories() != null) || feature.getCategories().length === 0) {
        this.featuresByType[feature.getType()]['uncategorized'].push(feature);
      }
      return this.featuresByType[feature.getType()]['all'].push(feature);
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
        return this.featuresByType[type]['all'];
      } else if (categories.length === 0) {
        return this.featuresByType[type]['uncategorized'];
      } else {
        features = new FeatureCollection({
          map: this.map
        });
        categories.forEach(function(category) {
          if (_this.featuresByType[type][category]) {
            return _this.featuresByType[type][category].forEach(function(feature) {
              if (!strict || !feature.getCategories() || feature.getCategories().length === 1) {
                return features.push(feature);
              }
            });
          }
        });
        return features;
      }
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

}).call(this);
