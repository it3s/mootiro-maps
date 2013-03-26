(function() {

  define(function(require) {
    'use strict';
    var $, Component, exports;
    $ = require('jquery');
    Component = (function() {

      Component.prototype.name = 'Base Component';

      Component.prototype.description = '';

      Component.prototype.hooks = {};

      Component.prototype.enabled = false;

      function Component(mediator, el) {
        this.mediator = mediator;
        this.el = el;
        this.map = this.mediator;
        this.$el = $(document).find(this.el);
      }

      Component.prototype.setMap = function(map) {
        this.map = map;
      };

      Component.prototype.enable = function() {
        return this.enabled = true;
      };

      Component.prototype.disable = function() {
        return this.enabled = false;
      };

      Component.prototype.init = function(opts) {
        return $.when(opts);
      };

      Component.prototype.destroy = function() {
        return true;
      };

      return Component;

    })();
    exports = Component;
    return exports;
  });

}).call(this);
