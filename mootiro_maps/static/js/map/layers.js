
define(function(require) {
  'use strict';
  var Collections, Layer, layers;
  Collections = require('./collections');
  Layer = (function() {

    function Layer(options) {
      this.options = options != null ? options : {};
      this.cache = new Collections.FeatureCollection();
      this.setName(this.options.name);
      this.setMap(this.options.map);
      this.setCollection(this.options.collection);
    }

    Layer.prototype.getName = function() {
      return this.name;
    };

    Layer.prototype.setName = function(name) {
      this.name = name;
      return this;
    };

    Layer.prototype.getCollection = function() {
      return this.collection;
    };

    Layer.prototype.setCollection = function(collection) {
      this.collection = collection;
      this.cache.clear();
      return this;
    };

    Layer.prototype.getRule = function() {
      return this.rule;
    };

    Layer.prototype.setRule = function(rule) {
      this.rule = rule;
      return this;
    };

    Layer.prototype.setMap = function(map) {
      var _base;
      this.map = map;
      return typeof (_base = this.cache).setMap === "function" ? _base.setMap(this.map) : void 0;
    };

    Layer.prototype.show = function() {
      return this.getFeatures().show();
    };

    Layer.prototype.hide = function() {
      return this.getFeatures().hide();
    };

    Layer.prototype.match = function(feature) {
      return feature.getType() === this.getName();
    };

    Layer.prototype.getFeatures = function() {
      if (this.cache.isEmpty) this.updateCache();
      return this.cache;
    };

    Layer.prototype.updateCache = function() {
      var filtered,
        _this = this;
      this.cache.clear();
      filtered = this.collection.filter(this.match, this);
      return filtered.forEach(function(feature) {
        return _this.cache.push(feature);
      });
    };

    return Layer;

  })();
  layers = {
    Layer: Layer
  };
  return layers;
});
