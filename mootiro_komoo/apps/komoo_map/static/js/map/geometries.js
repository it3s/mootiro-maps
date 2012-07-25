(function() {
  var EMPTY, Empty, Geometry, LineString, MULTIPOINT, MULTIPOLYLINE, MultiLineString, MultiPoint, POINT, POLYGON, POLYLINE, Point, Polygon, defaults, _base,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

  EMPTY = 'Empty';

  POINT = 'Point';

  MULTIPOINT = 'MultiPoint';

  POLYGON = 'Polygon';

  POLYLINE = 'LineString';

  MULTIPOLYLINE = 'MultiLineString';

  defaults = {
    BACKGROUND_COLOR: '#000',
    BACKGROUND_OPACITY: 0.6,
    BORDER_COLOR: '#000',
    BORDER_OPACITY: 0.6,
    BORDER_SIZE: 1.5,
    BORDER_SIZE_HOVER: 2.5,
    ZINDEX: 1
  };

  Geometry = (function() {

    function Geometry(options) {
      this.options = options != null ? options : {};
      this.setFeature(this.options.feature);
      this.initOverlay(this.options);
    }

    Geometry.prototype.initOverlay = function(options) {
      throw "Not Implemented";
    };

    Geometry.prototype.getCoordinates = function() {
      throw "Not Implemented";
    };

    Geometry.prototype.setCoordinates = function(coords) {
      return komoo.event.trigger(this, 'coordinates_changed');
    };

    Geometry.prototype.setEditable = function(flag) {
      throw "Not Implemented";
    };

    Geometry.prototype.initEvents = function(object) {
      var eventsNames,
        _this = this;
      if (object == null) object = this.overlay;
      if (!object) return;
      eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove', 'mouseout', 'mouseover', 'mouseup', 'rightclick'];
      return eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(object, eventName, function(e, args) {
          return komoo.event.trigger(_this, eventName, e, args);
        });
      });
    };

    Geometry.prototype.calculateBounds = function() {
      var bounds, coordinates, e, geometryType, getBounds, n, path, position, s, w, _i, _j, _len, _len2;
      n = s = w = e = null;
      getBounds = function(pos) {
        if (n == null) n = (s != null ? s : s = pos[0]);
        if (w == null) w = (e != null ? e : e = pos[1]);
        n = Math.max(pos[0], n);
        s = Math.min(pos[0], s);
        w = Math.min(pos[1], w);
        e = Math.max(pos[1], e);
        return [[s, w], [n, e]];
      };
      coordinates = this.getCoordinates();
      geometryType = this.getGeometryType();
      if (geometryType !== POLYGON && geometryType !== MULTIPOLYLINE) {
        coordinates = [coordinates];
      }
      for (_i = 0, _len = coordinates.length; _i < _len; _i++) {
        path = coordinates[_i];
        for (_j = 0, _len2 = path.length; _j < _len2; _j++) {
          position = path[_j];
          bounds = getBounds(position);
        }
      }
      if (bounds != null) {
        this.bounds = new google.maps.LatLngBounds(this.getLatLngFromArray(bounds[0]), this.getLatLngFromArray(bounds[1]));
      }
      return this.bounds;
    };

    Geometry.prototype.getBounds = function() {
      if (this.bounds != null) {
        return this.bounds;
      } else {
        return this.calculateBounds();
      }
    };

    Geometry.prototype.getCenter = function() {
      var _base2, _base3, _ref;
      if (!this.overlay) {
        return [];
      } else {
        return this.getArrayFromLatLng((typeof (_base2 = this.overlay).getCenter === "function" ? _base2.getCenter() : void 0) || ((_ref = this.getBounds()) != null ? _ref.getCenter() : void 0) || (typeof (_base3 = this.overlay).getPosition === "function" ? _base3.getPosition() : void 0));
      }
    };

    Geometry.prototype.getOverlay = function() {
      return this.overlay;
    };

    Geometry.prototype.setOverlay = function(overlay) {
      this.overlay = overlay;
      return this.initEvents();
    };

    Geometry.prototype.getFeature = function() {
      return this.feature;
    };

    Geometry.prototype.setFeature = function(feature) {
      this.feature = feature;
    };

    Geometry.prototype.getGeometryType = function() {
      return this.geometryType;
    };

    Geometry.prototype.getDefaultZIndex = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getDefaultZIndex() : void 0) || defaults.ZINDEX;
    };

    Geometry.prototype.getLatLngFromArray = function(pos) {
      if (pos != null) {
        return new google.maps.LatLng(pos[0], pos[1]);
      } else {
        return null;
      }
    };

    Geometry.prototype.getArrayFromLatLng = function(latLng) {
      if (latLng) {
        return [latLng.lat(), latLng.lng()];
      } else {
        return [];
      }
    };

    Geometry.prototype.getLatLngArrayFromArray = function(positions) {
      var pos, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = positions.length; _i < _len; _i++) {
        pos = positions[_i];
        _results.push(this.getLatLngFromArray(pos));
      }
      return _results;
    };

    Geometry.prototype.getArrayFromLatLngArray = function(latLngs) {
      var latLng, _i, _len, _results;
      if (latLngs) {
        _results = [];
        for (_i = 0, _len = latLngs.length; _i < _len; _i++) {
          latLng = latLngs[_i];
          _results.push(this.getArrayFromLatLng(latLng));
        }
        return _results;
      } else {
        return [];
      }
    };

    Geometry.prototype.getMap = function() {
      return this.map;
    };

    Geometry.prototype.setMap = function(map) {
      var _ref;
      this.map = map;
      return (_ref = this.overlay) != null ? _ref.setMap(this.map && this.map.googleMap ? this.map.googleMap : this.map) : void 0;
    };

    Geometry.prototype.getVisible = function() {
      var _ref;
      return (_ref = this.overlay) != null ? _ref.getVisible() : void 0;
    };

    Geometry.prototype.setVisible = function(flag) {
      var _ref;
      return (_ref = this.overlay) != null ? _ref.setVisible(flag) : void 0;
    };

    Geometry.prototype.setOptions = function(options) {
      var _ref;
      this.options = options;
      return (_ref = this.overlay) != null ? _ref.setOptions(this.options) : void 0;
    };

    Geometry.prototype.getIcon = function() {
      var _ref;
      return (_ref = this.overlay) != null ? typeof _ref.getIcon === "function" ? _ref.getIcon() : void 0 : void 0;
    };

    Geometry.prototype.setIcon = function(icon) {
      var _ref;
      return (_ref = this.overlay) != null ? typeof _ref.setIcon === "function" ? _ref.setIcon(icon) : void 0 : void 0;
    };

    Geometry.prototype.getGeoJson = function() {
      return {
        type: this.getGeometryType(),
        coordinates: this.getCoordinates()
      };
    };

    return Geometry;

  })();

  Empty = (function(_super) {

    __extends(Empty, _super);

    function Empty() {
      Empty.__super__.constructor.apply(this, arguments);
    }

    Empty.prototype.geometryType = EMPTY;

    Empty.prototype.initOverlay = function(options) {
      this.options = options != null ? options : {};
      return true;
    };

    Empty.prototype.getCoordinates = function() {
      return [];
    };

    Empty.prototype.setEditable = function(flag) {
      return true;
    };

    Empty.prototype.getGeoJson = function() {
      return null;
    };

    return Empty;

  })(Geometry);

  Point = (function(_super) {

    __extends(Point, _super);

    function Point() {
      Point.__super__.constructor.apply(this, arguments);
    }

    Point.prototype.geometryType = POINT;

    Point.prototype.initOverlay = function(options) {
      return this.setOverlay(new google.maps.Marker({
        clickable: options.clickable || true,
        zIndex: options.zIndex || this.getDefaultZIndex()
      }));
    };

    Point.prototype.initEvents = function(object) {
      var eventsNames,
        _this = this;
      if (object == null) object = this.overlay;
      Point.__super__.initEvents.call(this, object);
      eventsNames = ['animation_changed', 'clickable_changed', 'cursor_changed', 'drag', 'dragend', 'daggable_changed', 'dragstart', 'flat_changed', 'icon_changed', 'position_changed', 'shadow_changed', 'shape_changed', 'title_changed', 'visible_changed', 'zindex_changed'];
      return eventsNames.forEach(function(eventName) {
        return komoo.event.addListener(object, eventName, function(e, args) {
          return komoo.event.trigger(_this, eventName, e, args);
        });
      });
    };

    Point.prototype.getCoordinates = function() {
      return this.getArrayFromLatLng(this.overlay.getPosition());
    };

    Point.prototype.setCoordinates = function(coords) {
      this.bounds = null;
      this.overlay.setPosition(this.getLatLngFromArray(coords));
      return Point.__super__.setCoordinates.call(this, coords);
    };

    Point.prototype.setEditable = function(flag) {
      return this.overlay.setDraggable(flag);
    };

    Point.prototype.getPosition = function() {
      return this.overlay.getPosition();
    };

    Point.prototype.setPosition = function(pos) {
      return this.overlay.setPosition(pos instanceof Array ? this.getLatLngFromArray(pos) : pos);
    };

    return Point;

  })(Geometry);

  MultiPoint = (function(_super) {

    __extends(MultiPoint, _super);

    function MultiPoint() {
      MultiPoint.__super__.constructor.apply(this, arguments);
    }

    MultiPoint.prototype.geometryType = MULTIPOINT;

    MultiPoint.prototype.initOverlay = function(options) {
      return this.setOverlay(new MultiMarker({
        clickable: options.clickable || true,
        zIndex: options.zIndex || this.getDefaultZIndex()
      }));
    };

    MultiPoint.prototype.getPoints = function() {
      return this.overlay.getMarkers().getArray();
    };

    MultiPoint.prototype.setPoints = function(points) {
      return this.overlay.addMarkers(points);
    };

    MultiPoint.prototype.guaranteePoints = function(len) {
      var i, points, _ref, _ref2, _results, _results2;
      points = this.overlay.getMarkers();
      if (points.length >= len) {
        _results = [];
        for (i = 0, _ref = points.length - len - 1; 0 <= _ref ? i <= _ref : i >= _ref; 0 <= _ref ? i++ : i--) {
          _results.push(points.pop());
        }
        return _results;
      } else {
        _results2 = [];
        for (i = 0, _ref2 = len - points.length - 1; 0 <= _ref2 ? i <= _ref2 : i >= _ref2; 0 <= _ref2 ? i++ : i--) {
          _results2.push(this.overlay.addMarker(new google.maps.Marker(this.options)));
        }
        return _results2;
      }
    };

    MultiPoint.prototype.getCoordinates = function() {
      var point, _i, _len, _ref, _results;
      _ref = this.getPoints();
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        point = _ref[_i];
        _results.push(this.getArrayFromLatLng(point.getPosition()));
      }
      return _results;
    };

    MultiPoint.prototype.setCoordinates = function(coords) {
      var i, point, _len, _ref;
      if (!(coords[0] instanceof Array)) coords = [coords];
      this.guaranteePoints(coords.length);
      this.bounds = null;
      _ref = this.getPoints();
      for (i = 0, _len = _ref.length; i < _len; i++) {
        point = _ref[i];
        point.setPosition(this.getLatLngFromArray(coords[i]));
      }
      return MultiPoint.__super__.setCoordinates.call(this, coords);
    };

    MultiPoint.prototype.setEditable = function(flag) {
      return this.overlay.setDraggable(flag);
    };

    MultiPoint.prototype.getPositions = function() {
      var point, _i, _len, _ref, _results;
      _ref = this.getPoints();
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        point = _ref[_i];
        _results.push(point.getPosition());
      }
      return _results;
    };

    MultiPoint.prototype.setPositions = function(positions) {
      return this.overlay.setPositions(positions);
    };

    MultiPoint.prototype.getMarkers = function() {
      return this.overlay.getMarkers();
    };

    MultiPoint.prototype.addMarkers = function(markers) {
      return this.overlay.addMarkers(markers);
    };

    MultiPoint.prototype.addMarker = function(marker) {
      return this.overlay.addMarker(marker);
    };

    return MultiPoint;

  })(Geometry);

  LineString = (function(_super) {

    __extends(LineString, _super);

    LineString.prototype.geometryType = POLYLINE;

    function LineString(options) {
      LineString.__super__.constructor.call(this, options);
      this.handleEvents();
    }

    LineString.prototype.initOverlay = function(options) {
      return this.setOverlay(new google.maps.Polyline({
        clickable: options.clickable || true,
        zIndex: options.zIndex || this.getDefaultZIndex(),
        strokeColor: options.strokeColor || this.getBorderColor(),
        strokOpacity: options.strokeOpacity || this.getBorderOpacity(),
        strokeWeight: options.strokeWeight || this.getBorderSize()
      }));
    };

    LineString.prototype.handleEvents = function() {
      var _this = this;
      komoo.event.addListener(this, 'mousemove', function(e) {
        return _this.setOptions({
          strokeWeight: _this.getBorderSizeHover()
        });
      });
      return komoo.event.addListener(this, 'mouseout', function(e) {
        return _this.setOptions({
          strokeWeight: _this.getBorderSize()
        });
      });
    };

    LineString.prototype.getCoordinates = function() {
      var latLng, _i, _len, _ref, _results;
      _ref = this.overlay.getPath().getArray();
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        latLng = _ref[_i];
        _results.push(this.getArrayFromLatLng(latLng));
      }
      return _results;
    };

    LineString.prototype.setCoordinates = function(coords) {
      var pos;
      return this.overlay.setPath((function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = coords.length; _i < _len; _i++) {
          pos = coords[_i];
          _results.push(this.getLatLngFromArray(pos));
        }
        return _results;
      }).call(this));
    };

    LineString.prototype.setEditable = function(flag) {
      return this.overlay.setEditable(flag);
    };

    LineString.prototype.getBorderColor = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBorderColor() : void 0) || defaults.BORDER_COLOR;
    };

    LineString.prototype.getBorderOpacity = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBorderOpacity() : void 0) || defaults.BORDER_OPACITY;
    };

    LineString.prototype.getBorderSize = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBorderSize() : void 0) || defaults.BORDER_SIZE;
    };

    LineString.prototype.getBorderSizeHover = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBorderSizeHover() : void 0) || defaults.BORDER_SIZE_HOVER;
    };

    LineString.prototype.getPath = function() {
      return this.overlay.getPath();
    };

    LineString.prototype.setPath = function(path) {
      return this.overlay.setPath(path);
    };

    return LineString;

  })(Geometry);

  MultiLineString = (function(_super) {

    __extends(MultiLineString, _super);

    function MultiLineString() {
      MultiLineString.__super__.constructor.apply(this, arguments);
    }

    MultiLineString.prototype.geometryType = MULTIPOLYLINE;

    MultiLineString.prototype.initOverlay = function(options) {
      return this.setOverlay(new MultiPolyline({
        clickable: options.clickable || true,
        zIndex: options.zIndex || this.getDefaultZIndex(),
        strokeColor: options.strokeColor || this.getBorderColor(),
        strokOpacity: options.strokeOpacity || this.getBorderOpacity(),
        strokeWeight: options.strokeWeight || this.getBorderSize()
      }));
    };

    MultiLineString.prototype.guaranteeLines = function(len) {
      var i, lines, _ref, _ref2, _results, _results2;
      lines = this.overlay.getPolylines();
      if (lines.length >= len) {
        _results = [];
        for (i = 0, _ref = lines.length - len - 1; 0 <= _ref ? i <= _ref : i >= _ref; 0 <= _ref ? i++ : i--) {
          _results.push(lines.pop());
        }
        return _results;
      } else {
        _results2 = [];
        for (i = 0, _ref2 = len - lines.length - 1; 0 <= _ref2 ? i <= _ref2 : i >= _ref2; 0 <= _ref2 ? i++ : i--) {
          _results2.push(this.overlay.addPolyline(new google.maps.Polyline(this.options)));
        }
        return _results2;
      }
    };

    MultiLineString.prototype.getCoordinates = function() {
      var line, _i, _len, _ref, _results;
      _ref = this.overlay.getPolylines().getArray();
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        line = _ref[_i];
        _results.push(this.getArrayFromLatLngArray(line.getPath().getArray()));
      }
      return _results;
    };

    MultiLineString.prototype.setCoordinates = function(coords) {
      var i, line, _len, _ref, _results;
      if (!(coords[0][0] instanceof Array)) coords = [coords];
      this.guaranteeLines(coords.length);
      this.bounds = null;
      _ref = this.getLines();
      _results = [];
      for (i = 0, _len = _ref.length; i < _len; i++) {
        line = _ref[i];
        _results.push(line.setPath(this.getLatLngArrayFromArray(coords[i])));
      }
      return _results;
    };

    MultiLineString.prototype.getBorderSize = function() {
      return MultiLineString.__super__.getBorderSize.call(this) + 1;
    };

    MultiLineString.prototype.getBorderSizeHover = function() {
      return MultiLineString.__super__.getBorderSizeHover.call(this) + 1;
    };

    MultiLineString.prototype.getPath = function() {
      return this.getPaths().getAt(0);
    };

    MultiLineString.prototype.getPaths = function() {
      return this.overlay.getPaths();
    };

    MultiLineString.prototype.setPaths = function(paths) {
      return this.overlay.setPaths(paths);
    };

    MultiLineString.prototype.getLines = function() {
      return this.overlay.getPolylines().getArray();
    };

    MultiLineString.prototype.setLines = function(lines) {
      return this.overlay.addPolylines(lines);
    };

    MultiLineString.prototype.addPolyline = function(polyline, keep) {
      return this.overlay.addPolyline(polyline, keep);
    };

    return MultiLineString;

  })(LineString);

  Polygon = (function(_super) {

    __extends(Polygon, _super);

    function Polygon() {
      Polygon.__super__.constructor.apply(this, arguments);
    }

    Polygon.prototype.geometryType = POLYGON;

    Polygon.prototype.initOverlay = function(options) {
      return this.setOverlay(new google.maps.Polygon({
        clickable: options.clickable || true,
        zIndex: options.zIndex || this.getDefaultZIndex(),
        fillColor: options.fillColor || this.getBackgroundColor(),
        fillOpacity: options.fillOpacity || this.getBackgroundOpacity(),
        strokeColor: options.strokeColor || this.getBorderColor(),
        strokeOpacity: options.strokeOpacity || this.getBorderOpacity(),
        strokeWeight: options.strokeWeight || this.getBorderSize()
      }));
    };

    Polygon.prototype.getBackgroundColor = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBackgroundColor() : void 0) || defaults.BACKGROUND_COLOR;
    };

    Polygon.prototype.getBackgroundOpacity = function() {
      var _ref;
      return ((_ref = this.feature) != null ? _ref.getBackgroundOpacity() : void 0) || defaults.BACKGROUND_OPACITY;
    };

    Polygon.prototype.getCoordinates = function() {
      var coords, path, subCoords, _i, _len, _ref;
      coords = [];
      _ref = this.overlay.getPaths().getArray();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        path = _ref[_i];
        subCoords = this.getArrayFromLatLngArray(path.getArray());
        if (subCoords.length) subCoords.push(subCoords[0]);
        if (subCoords.length > 0) coords.push(subCoords);
      }
      return coords;
    };

    Polygon.prototype.setCoordinates = function(coords) {
      var path, paths, subCoords, _i, _len;
      paths = [];
      this.bounds = null;
      for (_i = 0, _len = coords.length; _i < _len; _i++) {
        subCoords = coords[_i];
        path = this.getLatLngArrayFromArray(subCoords);
        path.pop();
        paths.push(path);
      }
      return this.setPaths(paths);
    };

    Polygon.prototype.getPath = function() {
      return this.getPaths().getAt(0);
    };

    Polygon.prototype.getPaths = function() {
      return this.overlay.getPaths();
    };

    Polygon.prototype.setPaths = function(paths) {
      return this.overlay.setPaths(paths);
    };

    return Polygon;

  })(LineString);

  window.komoo.geometries = {
    Empty: Empty,
    Point: Point,
    MultiPoint: MultiPoint,
    LineString: LineString,
    MultiLineString: MultiLineString,
    Polygon: Polygon,
    defaults: defaults,
    makeGeometry: function(geojsonFeature, feature) {
      var coords, geometry, options, type;
      options = {
        feature: feature
      };
      if (!(geojsonFeature.geometry != null)) return new Empty(options);
      type = geojsonFeature.geometry.type;
      coords = geojsonFeature.geometry.coordinates;
      if (type === 'Point' || type === 'MultiPoint' || type === 'marker') {
        geometry = new MultiPoint(options);
      } else if (type === 'LineString' || type === 'polyline') {
        if (coords) coords = [coords];
        geometry = new MultiLineString(options);
      } else if (type === 'MultiLineString') {
        geometry = new MultiLineString(options);
      } else if (type === 'Polygon' || type === 'polygon') {
        geometry = new Polygon(options);
      }
      if (coords) if (geometry != null) geometry.setCoordinates(coords);
      return geometry;
    }
  };

}).call(this);
