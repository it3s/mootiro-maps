(function() {

  require(['map/geometries'], function(geometries) {
    test('Basic requirements', function() {
      expect(2);
      ok(Function.call, 'Function.call()');
      return ok(Object.create, 'Object.create()');
    });
    test('Get geometry default properties', function() {
      var simpleGeometry;
      expect(6);
      simpleGeometry = new geometries.Polygon();
      equal(simpleGeometry.getBackgroundColor(), geometries.defaults.BACKGROUND_COLOR, 'Should return the default background color');
      equal(simpleGeometry.getBackgroundOpacity(), geometries.defaults.BACKGROUND_OPACITY, 'Should return the default background opacity');
      equal(simpleGeometry.getBorderColor(), geometries.defaults.BORDER_COLOR, 'Should return the default border color');
      equal(simpleGeometry.getBorderOpacity(), geometries.defaults.BORDER_OPACITY, 'Should return the default border opacity');
      equal(simpleGeometry.getBorderSize(), geometries.defaults.BORDER_SIZE, 'Should return the default border size');
      return equal(simpleGeometry.getDefaultZIndex(), geometries.defaults.ZINDEX, 'Should return the default z-index');
    });
    test('Get geometry properties from "feature"', function() {
      var fakeFeature, simpleGeometry;
      expect(6);
      simpleGeometry = new geometries.Polygon();
      fakeFeature = {
        getBackgroundColor: function() {
          return '#fff';
        },
        getBackgroundOpacity: function() {
          return 0.5;
        },
        getBorderColor: function() {
          return '#ccc';
        },
        getBorderOpacity: function() {
          return 0.8;
        },
        getBorderSize: function() {
          return 10;
        },
        getDefaultZIndex: function() {
          return 100;
        }
      };
      simpleGeometry.setFeature(fakeFeature);
      equal(simpleGeometry.getBackgroundColor(), '#fff', 'Should return the background color from feature');
      equal(simpleGeometry.getBackgroundOpacity(), 0.5, 'Should return the background opacity from feature');
      equal(simpleGeometry.getBorderColor(), '#ccc', 'Should return the border color from feature');
      equal(simpleGeometry.getBorderOpacity(), 0.8, 'Should return the border opacity from feature');
      equal(simpleGeometry.getBorderSize(), 10, 'Should return the border size from feature');
      return equal(simpleGeometry.getDefaultZIndex(), 100, 'Should return the z-index from feature');
    });
    test('Create point geometry with googles marker object', function() {
      var simplePoint;
      expect(3);
      simplePoint = new geometries.Point();
      ok(simplePoint.overlay, 'Should create googleObject');
      ok(geometries.MultiMarker.prototype.isPrototypeOf(simplePoint.overlay), 'object should be a google.maps.Marker object');
      return equal(simplePoint.getGeometryType(), 'Point', 'Geometry type should be "Point"');
    });
    test('Create polyline geometry with googles polyline object', function() {
      var simplePolyline;
      expect(3);
      simplePolyline = new geometries.LineString();
      ok(simplePolyline.overlay, 'Should create googleObject');
      ok(google.maps.Polyline.prototype.isPrototypeOf(simplePolyline.overlay), 'object should be a google.maps.Polyline object');
      return equal(simplePolyline.getGeometryType(), 'LineString', 'Geometry type should be "LineString"');
    });
    test('Create polygon geometry with googles polygon object', function() {
      var simplePolygon;
      expect(3);
      simplePolygon = new geometries.Polygon();
      ok(simplePolygon.overlay, 'Should create googleObject');
      ok(google.maps.Polygon.prototype.isPrototypeOf(simplePolygon.overlay), 'object should be a google.maps.Polygon object');
      return equal(simplePolygon.getGeometryType(), 'Polygon', 'Geometry type should be "Polygon"');
    });
    test('Create multipoint geometry with MultiMarker object', function() {
      var simpleMultiPoint;
      expect(3);
      simpleMultiPoint = new geometries.MultiPoint();
      ok(simpleMultiPoint.overlay, 'Should create googleObject');
      ok(MultiMarker.prototype.isPrototypeOf(simpleMultiPoint.overlay), 'object should be a MultiMarker object');
      return equal(simpleMultiPoint.getGeometryType(), 'MultiPoint', 'Geometry type should be "MultiPoint"');
    });
    test('Set coordinates to point geometry', function() {
      var coordinates, point, position;
      expect(2);
      point = new geometries.Point();
      coordinates = [0, 1];
      point.setCoordinates(coordinates);
      position = point.overlay.getPosition();
      equal(position.lat(), coordinates[0]);
      return equal(position.lng(), coordinates[1]);
    });
    test('Get coordinates from point geometry', function() {
      var coordinates, point;
      expect(1);
      point = new geometries.Point();
      coordinates = [[1, 2]];
      point.setCoordinates(coordinates);
      return deepEqual(point.getCoordinates(), coordinates, 'Should return the same coordinates it received');
    });
    test('Get coordinates from empty point geometry', function() {
      var point;
      expect(1);
      point = new geometries.Point();
      return deepEqual(point.getCoordinates(), [], 'Should return null');
    });
    test('Set coordinates to polyline geometry', function() {
      var coordinates, googlePath, polyline;
      expect(10);
      polyline = new geometries.LineString();
      coordinates = [[0, 0], [0, 1], [1, 1], [1, 0], [1, 2]];
      polyline.setCoordinates(coordinates);
      googlePath = polyline.overlay.getPath();
      return googlePath.forEach(function(pos, i) {
        equal(pos.lat(), coordinates[i][0]);
        return equal(pos.lng(), coordinates[i][1]);
      });
    });
    test('Get coordinates from polyline geometry', function() {
      var coordinates, polyline;
      expect(1);
      polyline = new geometries.LineString();
      coordinates = [[0, 0], [0, 1], [1, 1], [1, 0], [1, 2]];
      polyline.setCoordinates(coordinates);
      return deepEqual(polyline.getCoordinates(), coordinates, 'Should return the same coordinates it received');
    });
    test('Get coordinates from empty polyline geometry', function() {
      var polyline;
      expect(1);
      polyline = new geometries.LineString();
      return deepEqual(polyline.getCoordinates(), [], 'Should return an empty array');
    });
    test('Set coordinates to polygon geometry', function() {
      var coordinates, googlePaths, polygon;
      expect(16);
      polygon = new geometries.Polygon();
      coordinates = [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], [[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]]];
      polygon.setCoordinates(coordinates);
      googlePaths = polygon.overlay.getPaths();
      return googlePaths.forEach(function(path, i) {
        return path.forEach(function(pos, j) {
          equal(pos.lat(), coordinates[i][j][0]);
          return equal(pos.lng(), coordinates[i][j][1]);
        });
      });
    });
    test('Get coordinates from polygon geometry', function() {
      var coordinates, polygon;
      expect(1);
      polygon = new geometries.Polygon();
      coordinates = [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]], [[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]]];
      polygon.setCoordinates(coordinates);
      return deepEqual(polygon.getCoordinates(), coordinates, 'Should return the same coordinates it received');
    });
    test('Get coordinates from empty polygon geometry', function() {
      var polygon;
      expect(1);
      polygon = new geometries.Polygon();
      return deepEqual(polygon.getCoordinates(), [], 'Should return an empty array');
    });
    test('Set coordinates to multpoint geometry', function() {
      var coordinates, multiPoint, positions;
      expect(4);
      multiPoint = new geometries.MultiPoint();
      coordinates = [[0, 1], [3, 4]];
      multiPoint.setCoordinates(coordinates);
      positions = multiPoint.getPositions();
      equal(positions[0].lat(), coordinates[0][0]);
      equal(positions[0].lng(), coordinates[0][1]);
      equal(positions[1].lat(), coordinates[1][0]);
      return equal(positions[1].lng(), coordinates[1][1]);
    });
    test('Get coordinates from multipoint geometry', function() {
      var coordinates, multiPoint;
      expect(1);
      multiPoint = new geometries.MultiPoint();
      coordinates = [[0, 1], [3, 4]];
      multiPoint.setCoordinates(coordinates);
      return deepEqual(multiPoint.getCoordinates(), coordinates, 'Should return the same coordinates it received');
    });
    test('Get coordinates from empty multipoint geometry', function() {
      var multiPoint;
      expect(1);
      multiPoint = new geometries.MultiPoint();
      return deepEqual(multiPoint.getCoordinates(), [], 'Should return an empty array');
    });
    return test('Geometry factory', function() {
      var point, pointFeature, polygon, polygonFeature, polyline, polylineFeature;
      expect(3);
      pointFeature = {
        'type': 'Feature',
        'geometry': {
          'type': 'Point',
          'coordinates': [1, 2]
        },
        'properties': null
      };
      point = geometries.makeGeometry(pointFeature);
      ok(point instanceof geometries.MultiPoint, 'Geometry object shoud be an instance of geometries.MultiPoint');
      polylineFeature = {
        'type': 'Feature',
        'geometry': {
          'type': 'LineString',
          'coordinates': [[0, 0], [1, 1], [1, 2]]
        },
        'properties': null
      };
      polyline = geometries.makeGeometry(polylineFeature);
      ok(polyline instanceof geometries.MultiLineString, 'Geometry object shoud be an instance of geometries.MultiLineString');
      polygonFeature = {
        'type': 'Feature',
        'geometry': {
          'type': 'Polygon',
          'coordinates': [[[0, 0], [1, 1], [1, 2], [0, 0]]]
        },
        'properties': null
      };
      polygon = geometries.makeGeometry(polygonFeature);
      return ok(polygon instanceof geometries.Polygon, 'Geometry object shoud be an instance of geometries.Polygon');
    });
  });

}).call(this);
