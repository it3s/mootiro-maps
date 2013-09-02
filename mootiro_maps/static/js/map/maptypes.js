(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var CleanMapType, Component, googleMaps, _base;
    googleMaps = require('googlemaps');
    Component = require('./component');
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
    CleanMapType = (function(_super) {

      __extends(CleanMapType, _super);

      CleanMapType.prototype.id = 'clean';

      function CleanMapType() {
        this.mapType = new googleMaps.StyledMapType([
          {
            featureType: 'poi',
            elementType: 'all',
            stylers: [
              {
                visibility: "off"
              }
            ]
          }, {
            featureType: 'road',
            elementType: 'all',
            stylers: [
              {
                lightness: 70
              }
            ]
          }, {
            featureType: 'transit',
            elementType: 'all',
            stylers: [
              {
                lightness: 50
              }
            ]
          }, {
            featureType: 'water',
            elementType: 'all',
            stylers: [
              {
                lightness: 50
              }
            ]
          }, {
            featureType: 'administrative',
            elementType: 'labels',
            stylers: [
              {
                lightness: 30
              }
            ]
          }
        ], {
          name: gettext('Clean')
        });
      }

      CleanMapType.prototype.setMap = function(map) {
        var options;
        this.map = map;
        this.map.googleMap.mapTypes.set(this.id, this.mapType);
        options = this.map.googleMap.mapTypeControlOptions;
        options.mapTypeIds.push(this.id);
        this.map.googleMap.setOptions({
          mapTypeControlOptions: options
        });
        return this.map.publish('maptype_loaded', this.id);
      };

      return CleanMapType;

    })(Component);
    window.komoo.maptypes = {
      CleanMapType: CleanMapType
    };
    return window.komoo.maptypes;
  });

}).call(this);
