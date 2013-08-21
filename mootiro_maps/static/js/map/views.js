(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    var Backbone, LayersBoxView, SearchBoxView, _;
    _ = require('underscore');
    Backbone = require('backbone');
    SearchBoxView = (function(_super) {

      __extends(SearchBoxView, _super);

      function SearchBoxView() {
        SearchBoxView.__super__.constructor.apply(this, arguments);
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
        if (type == null) type = 'address';
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
        LayersBoxView.__super__.constructor.apply(this, arguments);
      }

      LayersBoxView.prototype.events = {
        'click .layer': 'toggleLayer'
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
        return this;
      };

      LayersBoxView.prototype.toggleLayer = function(evt) {
        var $el, layer, layerId, visible;
        $el = this.$(evt.currentTarget);
        layerId = $el.attr('data-layer');
        layer = this.layers.getLayer(layerId);
        visible = layer.toggle();
        $el.attr('data-visible', visible);
        return $el.find('.layer-icon').attr('src', layer.getIconUrl());
      };

      return LayersBoxView;

    })(Backbone.View);
    return {
      SearchBoxView: SearchBoxView,
      LayersBoxView: LayersBoxView
    };
  });

}).call(this);
