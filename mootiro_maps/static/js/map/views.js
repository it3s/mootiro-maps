// Generated by CoffeeScript 1.4.0
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(function(require) {
  var Backbone, LayersBoxView, SearchBoxView, _;
  _ = require('underscore');
  Backbone = require('backbone');
  SearchBoxView = (function(_super) {

    __extends(SearchBoxView, _super);

    function SearchBoxView() {
      return SearchBoxView.__super__.constructor.apply(this, arguments);
    }

    SearchBoxView.prototype.events = {
      'click .search': 'onSearchBtnClick',
      'change .location-type': 'onTypeChange'
    };

    SearchBoxView.prototype.initialize = function() {
      return this.template = _.template(require('text!templates/map/_searchbox.html'));
    };

    SearchBoxView.prototype.render = function() {
      var renderedContent;
      renderedContent = this.template();
      this.$el.html(renderedContent);
      return this;
    };

    SearchBoxView.prototype.onTypeChange = function() {
      var type;
      type = this.$('.location-type').val();
      if (type === 'address') {
        this.$('.latLng-container').hide();
        return this.$('.address-container').show();
      } else {
        this.$('.address-container').hide();
        return this.$('.latLng-container').show();
      }
    };

    SearchBoxView.prototype.onSearchBtnClick = function() {
      var position, type;
      type = this.$('.location-type').val();
      position = type === 'address' ? this.$('.address').val() : [parseFloat(this.$('.lat').val().replace(',', '.')), parseFloat(this.$('.lng').val().replace(',', '.'))];
      this.search(type, position);
      return false;
    };

    SearchBoxView.prototype.search = function(type, position) {
      if (type == null) {
        type = 'address';
      }
      this.trigger('search', {
        type: type,
        position: position
      });
      return this;
    };

    return SearchBoxView;

  })(Backbone.View);
  LayersBoxView = (function(_super) {

    __extends(LayersBoxView, _super);

    function LayersBoxView() {
      return LayersBoxView.__super__.constructor.apply(this, arguments);
    }

    LayersBoxView.prototype.events = {
      'click .layer .item': 'toggleLayer',
      'click .layer .collapser': 'toggleSublist',
      'click .feature': 'highlightFeature'
    };

    LayersBoxView.prototype.initialize = function() {
      return this.template = _.template(require('text!templates/map/_layersbox.html'));
    };

    LayersBoxView.prototype.render = function(layers) {
      var renderedContent;
      this.layers = layers;
      renderedContent = this.template({
        layers: this.layers
      });
      this.$el.html(renderedContent);
      this.$('.sublist').hide();
      return this;
    };

    LayersBoxView.prototype.updateCounters = function(layers) {
      var _this = this;
      return layers.forEach(function(layer) {
        return _this.$('[data-layer=' + layer.getId() + '] .length').text(layer.countFeatures());
      });
    };

    LayersBoxView.prototype.updateSublists = function(layers) {
      var _this = this;
      return layers.forEach(function(layer) {
        var $sublist, $sublistUl;
        if (layer.countFeatures()) {
          _this.$('[data-layer=' + layer.getId() + ']').parent().find('.collapser').show();
          $sublist = _this.$('.sublist[data-layer=' + layer.getId() + ']');
          $sublistUl = $sublist.find('ul').empty();
          return layer.getFeatures().forEach(function(feature) {
            return $sublistUl.append('<li class="feature" data-type="' + feature.getProperty('type') + '" data-id="' + feature.getProperty('id') + '">' + feature.getProperty('name') + '</li>');
          });
        }
      });
    };

    LayersBoxView.prototype.toggleLayer = function(evt) {
      var $el, action, isVisible, layerId;
      $el = this.$(evt.currentTarget);
      layerId = $el.attr('data-layer');
      isVisible = $el.attr('data-visible') === 'true';
      action = !isVisible ? 'show' : 'hide';
      this.trigger(action, layerId);
      $el.attr('data-visible', !isVisible);
      return $el.toggleClass('on off');
    };

    LayersBoxView.prototype.toggleSublist = function(evt) {
      var $collapser, $sublist;
      $collapser = this.$(evt.currentTarget);
      $sublist = $collapser.parent().next('.sublist');
      console.log($sublist);
      $collapser.find('i').toggleClass('icon-chevron-right icon-chevron-down');
      return $sublist.toggle();
    };

    LayersBoxView.prototype.highlightFeature = function(evt) {
      var $el, id, type;
      $el = this.$(evt.currentTarget);
      type = $el.attr('data-type');
      id = parseInt($el.attr('data-id'));
      return this.trigger('highlight_feature', type, id);
    };

    return LayersBoxView;

  })(Backbone.View);
  return {
    SearchBoxView: SearchBoxView,
    LayersBoxView: LayersBoxView
  };
});
