(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(['map/component'], function(Component) {
    'use strict';
    var CleanMapType, _base;
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = google.maps.event;
    CleanMapType = (function(_super) {

      __extends(CleanMapType, _super);

      CleanMapType.prototype.id = 'clean';

      function CleanMapType() {
        this.mapType = new google.maps.StyledMapType([
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
        return this.map.googleMap.setMapTypeId(this.id);
      };

      return CleanMapType;

    })(Component);
    window.komoo.maptypes = {
      CleanMapType: CleanMapType
    };
    return window.komoo.maptypes;
  });

}).call(this);
