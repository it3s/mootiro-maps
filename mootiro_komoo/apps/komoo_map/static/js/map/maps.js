(function() {
  var AjaxEditor, AjaxMap, Editor, SimpleMap, _base,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

  SimpleMap = (function() {

    SimpleMap.prototype.googleMapDefaultOptions = {
      zoom: 12,
      center: new google.maps.LatLng(-23.55, -46.65),
      disableDefaultUI: false,
      streetViewControl: true,
      scaleControl: true,
      panControlOptions: {
        position: google.maps.ControlPosition.RIGHT_TOP
      },
      zoomControlOptions: {
        position: google.maps.ControlPosition.RIGHT_TOP
      },
      scaleControlOptions: {
        position: google.maps.ControlPosition.RIGHT_BOTTOM,
        style: google.maps.ScaleControlStyle.DEFAULT
      },
      mapTypeControlOptions: {
        mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.HYBRID]
      },
      mapTypeId: google.maps.MapTypeId.HYBRID
    };

    function SimpleMap(options) {
      this.options = options != null ? options : {};
      this.element = document.getElementById(this.options.elementId);
      this.features = komoo.collections.makeFeatureCollectionPlus({
        map: this
      });
      this.providers = [];
      this.mapTypes = [];
      this.initGoogleMap(this.options.googleMapOptions);
      this.initFeatureTypes();
      this.initProviders();
      this.initControls();
      this.handleEvents();
    }

    SimpleMap.prototype.initGoogleMap = function(options) {
      if (options == null) options = this.googleMapDefaultOptions;
      return this.googleMap = new google.maps.Map(this.element, options);
    };

    SimpleMap.prototype.initFeatureTypes = function() {
      var _ref,
        _this = this;
      if (this.featureTypes == null) this.featureTypes = {};
      return (_ref = this.options.featureTypes) != null ? _ref.forEach(function(type) {
        return _this.featureTypes[type.type] = type;
      }) : void 0;
    };

    SimpleMap.prototype.initProviders = function() {};

    SimpleMap.prototype.initControls = function() {};

    SimpleMap.prototype.handleEvents = function() {};

    SimpleMap.prototype.addProvider = function(provider) {
      provider.setMap(this);
      return this.providers.push(provider);
    };

    SimpleMap.prototype.addMapType = function(mapType) {
      mapType.setMap(this);
      return this.mapTypes.push(mapType);
    };

    SimpleMap.prototype.clear = function() {
      this.features.removeAllFromMap();
      return this.features.clear();
    };

    SimpleMap.prototype.refresh = function() {
      return google.maps.event.trigger(this.googleMap, 'resize');
    };

    SimpleMap.prototype.saveLocation = function(center, zoom) {
      if (center == null) center = this.googleMap.getCenter();
      if (zoom == null) zoom = this.getZoom();
      komoo.utils.createCookie('lastLocation', center.toUrlValue(), 90);
      return komoo.utils.createCookie('lastZoom', zoom, 90);
    };

    SimpleMap.prototype.goToSavedLocation = function() {
      var center, lastLocation, zoom;
      lastLocation = komoo.utils.readCookie('lastLocation');
      zoom = parseInt(komoo.utils.readCookie('lastZoom'), 10);
      if (lastLocation && zoom) {
        if (typeof console !== "undefined" && console !== null) {
          console.log('Getting location from cookie...');
        }
        lastLocation = lastLocation.split(',');
        center = new google.maps.LatLng(lastLocation[0], lastLocation[1]);
        this.googleMap.setCenter(center);
        this.googleMap.setZoom(zoom);
      }
      return true;
    };

    false;

    SimpleMap.prototype.goToUserLocation = function() {
      var clientLocation, pos,
        _this = this;
      if (clientLocation = google.loader.ClientLocation) {
        pos = new google.maps.LatLng(clientLocation.latitude, clientLocation.longitude);
        this.googleMap.setCenter(pos);
        if (typeof console !== "undefined" && console !== null) {
          console.log('Getting location from Google...');
        }
      }
      if (navigator.geolocation) {
        return navigator.geolocation.getCurrentPosition(function(position) {
          pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
          _this.googleMap.setCenter(pos);
          return typeof console !== "undefined" && console !== null ? console.log('Getting location from navigator.geolocation...') : void 0;
        }, function() {
          return typeof console !== "undefined" && console !== null ? console.log('User denied access to navigator.geolocation...') : void 0;
        });
      }
    };

    SimpleMap.prototype.handleFeatureEvents = function(feature) {};

    SimpleMap.prototype.loadGeoJSON = function(geojson, panTo, attach) {
      var features, _ref, _ref2,
        _this = this;
      if (panTo == null) panTo = false;
      if (attach == null) attach = true;
      if (!((geojson != null ? geojson.type : void 0) != null)) return [];
      if (!geojson.type === 'FeatureCollection') return [];
      features = komoo.collections.makeFeatureCollection({
        map: this
      });
      if ((_ref = geojson.features) != null) {
        _ref.forEach(function(geojsonFeature) {
          var feature;
          feature = _this.features.getById(geojsonFeature.properties.type, geojsonFeature.properties.id);
          if (feature == null) {
            feature = komoo.features.makeFeature(geojsonFeature, _this.featureTypes);
          }
          features.push(feature);
          _this.handleFeatureEvents(feature);
          if (attach) {
            _this.features.push(feature);
            return feature.setMap(_this);
          }
        });
      }
      if (panTo && ((_ref2 = features.getAt(0)) != null ? _ref2.getBounds() : void 0)) {
        this.googleMap.fitBounds(features.getAt(0).getBounds());
      }
      return features;
    };

    SimpleMap.prototype.getGeoJSON = function(options) {
      var list;
      if (options == null) options = {};
      if (options.newOnly == null) options.newOnly = false;
      if (options.currentOnly == null) options.currentOnly = false;
      if (options.geometryCollection == null) options.geometryCollection = false;
      list = options.newOnly ? this.newFeatures : options.currentOnly ? komoo.collections.makeFeatureCollection({
        map: this.map,
        features: [this.currentFeature]
      }) : this.features;
      return list.getGeoJson({
        geometryCollection: options.geometryCollection
      });
    };

    SimpleMap.prototype.getBounds = function() {
      return this.googleMap.getBounds();
    };

    SimpleMap.prototype.getZoom = function() {
      return this.googleMap.getZoom();
    };

    return SimpleMap;

  })();

  Editor = (function(_super) {

    __extends(Editor, _super);

    function Editor() {
      Editor.__super__.constructor.apply(this, arguments);
    }

    return Editor;

  })(SimpleMap);

  AjaxMap = (function(_super) {

    __extends(AjaxMap, _super);

    function AjaxMap() {
      AjaxMap.__super__.constructor.apply(this, arguments);
    }

    AjaxMap.prototype.initProviders = function() {
      AjaxMap.__super__.initProviders.call(this);
      return this.addProvider(komoo.providers.makeFeatureProvider());
    };

    return AjaxMap;

  })(SimpleMap);

  AjaxEditor = (function(_super) {

    __extends(AjaxEditor, _super);

    function AjaxEditor() {
      AjaxEditor.__super__.constructor.apply(this, arguments);
    }

    AjaxEditor.prototype.initProviders = function() {
      AjaxEditor.__super__.initProviders.call(this);
      return this.addProvider(komoo.providers.makeFeatureProvider());
    };

    return AjaxEditor;

  })(Editor);

  window.komoo.maps = {
    SimpleMap: SimpleMap,
    AjaxMap: AjaxMap,
    makeMap: function(options) {
      if (options == null) options = {};
      return new AjaxMap(options);
    }
  };

}).call(this);
