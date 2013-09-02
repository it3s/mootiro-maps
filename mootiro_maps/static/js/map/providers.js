(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var Component, FeatureProvider, GenericProvider, ZoomFilteredFeatureProvider, googleMaps, _base;
    googleMaps = require('googlemaps');
    Component = require('./component');
    if (window.komoo == null) window.komoo = {};
    if ((_base = window.komoo).event == null) _base.event = googleMaps.event;
    GenericProvider = (function(_super) {

      __extends(GenericProvider, _super);

      function GenericProvider() {
        GenericProvider.__super__.constructor.apply(this, arguments);
      }

      GenericProvider.prototype.name = 'Generic Provider';

      GenericProvider.prototype.alt = 'Generic Data Provider';

      GenericProvider.prototype.tileSize = new googleMaps.Size(256, 256);

      GenericProvider.prototype.maxZoom = 32;

      GenericProvider.prototype.expiration = 600000;

      GenericProvider.prototype.enabled = true;

      GenericProvider.prototype.init = function(options) {
        this.options = options;
        this.addrLatLngCache = {};
        return this.fetchedTiles = {};
      };

      GenericProvider.prototype.setMap = function(map) {
        this.map = map;
        this.map.googleMap.overlayMapTypes.insertAt(0, this);
        return typeof this.handleMapEvents === "function" ? this.handleMapEvents() : void 0;
      };

      GenericProvider.prototype.enable = function() {
        return this.enabled = true;
      };

      GenericProvider.prototype.disable = function() {
        return this.enabled = false;
      };

      GenericProvider.prototype.getUrl = function(coord, zoom) {
        var addr, baseUrl;
        addr = this.getAddrLatLng(coord, zoom);
        baseUrl = this.fetchUrl + addr;
        if (this.map.getProjectId()) {
          baseUrl += '&project=' + this.map.getProjectId();
        }
        return baseUrl;
      };

      GenericProvider.prototype.getAddrLatLng = function(coord, zoom) {
        var key, ne, numTiles, point1, point2, projection, sw;
        key = "x=" + coord.x + ",y=" + coord.y + ",z=" + zoom;
        if (this.addrLatLngCache[key]) return this.addrLatLngCache[key];
        numTiles = 1 << zoom;
        projection = this.map.googleMap.getProjection();
        point1 = new googleMaps.Point((coord.x + 1) * this.tileSize.width / numTiles, coord.y * this.tileSize.height / numTiles);
        point2 = new googleMaps.Point(coord.x * this.tileSize.width / numTiles, (coord.y + 1) * this.tileSize.height / numTiles);
        ne = projection.fromPointToLatLng(point1);
        sw = projection.fromPointToLatLng(point2);
        return this.addrLatLngCache[key] = "bounds=" + (ne.toUrlValue()) + "," + (sw.toUrlValue()) + "&zoom=" + zoom;
      };

      return GenericProvider;

    })(Component);
    FeatureProvider = (function(_super) {

      __extends(FeatureProvider, _super);

      function FeatureProvider() {
        FeatureProvider.__super__.constructor.apply(this, arguments);
      }

      FeatureProvider.prototype.name = 'Feature Provider';

      FeatureProvider.prototype.alt = 'Feature Provider';

      FeatureProvider.prototype.fetchUrl = '/get_geojson?';

      FeatureProvider.prototype.init = function(options) {
        FeatureProvider.__super__.init.call(this, options);
        this.keptFeatures = komoo.collections.makeFeatureCollection();
        this.openConnections = 0;
        this._addrs = [];
        return this._requestQueue = {};
      };

      FeatureProvider.prototype.handleMapEvents = function() {
        var _this = this;
        this.map.subscribe('idle', function() {
          var bounds;
          bounds = _this.map.googleMap.getBounds();
          _this.keptFeatures.forEach(function(feature) {
            if (!bounds.intersects(feature.getBounds())) {
              return feature.setMap(null);
            }
          });
          return _this.keptFeatures.clear();
        });
        return this.map.subscribe('zoom_changed', function() {
          var addr, xhr, _ref, _results;
          _ref = _this._requestQueue;
          _results = [];
          for (addr in _ref) {
            xhr = _ref[addr];
            _results.push(xhr.abort());
          }
          return _results;
        });
      };

      FeatureProvider.prototype.releaseTile = function(tile) {
        var bounds;
        if (this.enabled === false) return;
        if (this.fetchedTiles[tile.addr]) {
          bounds = this.map.getBounds();
          return this.map.data.when(this.fetchedTiles[tile.addr].features, function(features) {
            var _this = this;
            return features.forEach(function(feature) {
              if (feature.getBounds) {
                if (!bounds.intersects(feature.getBounds())) {
                  return feature.setMap(null);
                } else if (!bounds.contains(feature.getBounds().getNorthEast() || !bounds.contains(feature.getBounds().getSouthWest()))) {
                  _this.keptFeatures.push(feature);
                  return feature.setMap(_this.map);
                }
              } else if (feature.getPosition) {
                if (!bounds.contains(feature.getPosition())) {
                  feature.setVisible(false);
                  return feature.setMap(null);
                }
              }
            });
          });
        }
      };

      FeatureProvider.prototype.getTile = function(coord, zoom, ownerDocument) {
        var addr, d, div, _base2,
          _this = this;
        div = ownerDocument.createElement('DIV');
        addr = this.getAddrLatLng(coord, zoom);
        div.addr = addr;
        if (this.enabled === false || this.map.options.ajax === false) {
          this.map.publish('features_request_completed');
          return div;
        }
        d = new Date();
        if (this.fetchedTiles[addr] && (d - this.fetchedTiles[addr].date <= this.expiration)) {
          if (typeof (_base2 = this.fetchedTiles[addr].features).setMap === "function") {
            _base2.setMap(this.map);
          }
          return div;
        }
        if (this.openConnections === 0) {
          this.map.publish('features_request_started');
        }
        this.openConnections++;
        this.map.publish('features_request_queued');
        this._requestQueue[addr] = $.ajax({
          url: this.getUrl(coord, zoom),
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            var dfd;
            dfd = _this.map.data.deferred();
            _this._addrs.push(addr);
            return _this.fetchedTiles[addr] = {
              geojson: data,
              features: dfd.promise(),
              date: new Date()
            };
          },
          error: function(jqXHR, textStatus) {
            var errorContainer, serverErrorContainer;
            if (textStatus === 'abort') return;
            if (typeof console !== "undefined" && console !== null) {
              console.error("[provider - ajax error] " + textStatus);
            }
            serverErrorContainer = $('#server-error');
            if (serverErrorContainer.parent().length === 0) {
              serverErrorContainer = $('<div>').attr('id', 'server-error');
              $('body').append(serverErrorContainer);
            }
            errorContainer = $('<div>').html(jqXHR.responseText);
            return serverErrorContainer.append(errorContainer);
          },
          complete: function() {
            var data, features, _base3;
            _this.map.publish('features_request_unqueued');
            _this.openConnections--;
            if (_this.openConnections === 0) {
              _this.map.publish('features_request_completed');
              while (_this._addrs.length > 0) {
                addr = _this._addrs.pop();
                data = _this.fetchedTiles[addr].geojson;
                features = _this.map.loadGeoJSON(JSON.parse(data), false, true, true);
                if (typeof (_base3 = _this.fetchedTiles[addr].features).resolve === "function") {
                  _base3.resolve(features);
                }
                _this.fetchedTiles[addr].features = features;
              }
              delete _this._requestQueue[addr];
              return _this.map.publish('features_loaded', _this.map.getFeatures());
            }
          }
        });
        return div;
      };

      return FeatureProvider;

    })(GenericProvider);
    ZoomFilteredFeatureProvider = (function(_super) {

      __extends(ZoomFilteredFeatureProvider, _super);

      function ZoomFilteredFeatureProvider() {
        ZoomFilteredFeatureProvider.__super__.constructor.apply(this, arguments);
      }

      ZoomFilteredFeatureProvider.prototype.getUrl = function(coord, zoom) {
        var baseUrl, featureType, featureTypeName, models, _ref;
        baseUrl = ZoomFilteredFeatureProvider.__super__.getUrl.call(this, coord, zoom);
        models = [];
        _ref = this.map.featureTypes;
        for (featureTypeName in _ref) {
          featureType = _ref[featureTypeName];
          if ((this.map.getProjectId() != null) || featureTypeName === 'Community' || (featureType.minZoomPoint <= zoom && featureType.maxZoomPoint >= zoom) || (featureType.minZoomGeometry <= zoom && featureType.maxZoomGeometry >= zoom)) {
            models.push("" + featureType.appLabel + "." + featureType.modelName);
          }
        }
        return baseUrl += '&models=' + models.join(',');
      };

      return ZoomFilteredFeatureProvider;

    })(FeatureProvider);
    window.komoo.providers = {
      GenericProvider: GenericProvider,
      FeatureProvider: FeatureProvider,
      ZoomFilteredFeatureProvider: ZoomFilteredFeatureProvider,
      makeFeatureProvider: function(options) {
        return new FeatureProvider(options);
      }
    };
    return window.komoo.providers;
  });

}).call(this);
