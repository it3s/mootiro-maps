var __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(function(require) {
  'use strict';
  var Collections, Layer, eval_expr, layers;
  Collections = require('./collections');
  eval_expr = function(expr, obj) {
    var operator, res, v, _i, _len, _ref, _ref2, _ref3;
    if (!(expr != null) || !(obj != null)) return false;
    operator = expr.operator;
    if (operator === '==' || operator === 'is' || operator === 'equal' || operator === 'equals') {
      return obj.getProperty(expr.property) === expr.value;
    } else if (operator === '!=' || operator === 'isnt' || operator === 'not equal' || operator === 'not equals' || operator === 'different') {
      return !obj.getProperty(expr.property) === expr.value;
    } else if (operator === 'in') {
      return _ref = obj.getProperty(expr.property), __indexOf.call(expr.value, _ref) >= 0;
    } else if ((operator === 'contains' || operator === 'has') && Object.prototype.toString.call(expr.value) === '[object Array]') {
      res = true;
      _ref2 = expr.value;
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        v = _ref2[_i];
        res = res && __indexOf.call(obj.getProperty(expr.property), v) >= 0;
      }
      return res;
    } else if (operator === 'contains' || operator === 'has') {
      return _ref3 = expr.value, __indexOf.call(obj.getProperty(expr.property), _ref3) >= 0;
    } else if (operator === '!' || operator === 'not') {
      return !obj.getProperty(expr.child, obj);
    } else if (operator === 'or') {
      return eval_expr(expr.left, obj) || eval_expr(expr.right, obj);
    } else if (operator === 'and') {
      return eval_expr(expr.left, obj) && eval_expr(expr.right, obj);
    }
  };
  window.ee = eval_expr;
  Layer = (function() {

    function Layer(options) {
      this.options = options != null ? options : {};
      this.cache = new Collections.FeatureCollection();
      this.setName(this.options.name);
      this.setRule(this.options.rule);
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
      return eval_expr(this.rule, feature);
    };

    Layer.prototype.getFeatures = function() {
      if (this.cache.isEmpty()) this.updateCache();
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
