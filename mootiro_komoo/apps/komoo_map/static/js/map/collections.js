(function() {
  var FeatureCollection, GenericCollection, Layer, _base,
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

    return GenericCollection;

  })();

  FeatureCollection = (function(_super) {

    __extends(FeatureCollection, _super);

    function FeatureCollection(options) {
      if (options == null) options = {};
      FeatureCollection.__super__.constructor.call(this, options);
      if (options.map) this.setMap(options.map);
      if (options.features) {
        options.features.forEach(function(feature) {
          return this.push(feature);
        });
      }
    }

    FeatureCollection.prototype.push = function(feature) {
      FeatureCollection.__super__.push.call(this, feature);
      return feature.setMap(this.map);
    };

    FeatureCollection.prototype.setMap = function(map, opt_force) {
      var _this = this;
      this.map = map;
      this.forEach(function(feature) {
        return feature.setMap(_this.map, opt_force);
      });
      return this.handleMapEvents();
    };

    FeatureCollection.prototype.show = function() {
      this.setMap(this.map, {
        geometries: true
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
    makeFeatureCollection: function(options) {
      if (options == null) options = {};
      return new FeatureCollection(options);
    }
  };

}).call(this);
