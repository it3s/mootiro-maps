(function() {

  require(['map/features'], function(features) {
    var _this = this;
    module('Map Features');
    test('Basic requirements', function() {
      expect(3);
      ok(Function.call, 'Function.call()');
      ok(Object.create, 'Object.create()');
      return ok(google.maps, 'Google maps API');
    });
    return test('Get geoJson geometry from feature', function() {
      var coordinates, feature, geometry, point;
      expect(1);
      coordinates = [1, 2];
      point = {
        getGeometryType: function() {
          return 'Point';
        },
        getCoordinates: function() {
          return coordinates;
        },
        getGeoJson: function() {
          return {
            type: this.getGeometryType(),
            coordinates: this.getCoordinates()
          };
        }
      };
      feature = new features.Feature();
      geometry = {
        'type': 'Point',
        'coordinates': coordinates
      };
      feature.setGeometry(point);
      return deepEqual(feature.getGeoJsonGeometry(), geometry, 'Should return the geometry containing the coordinates it received');
    });
  });

}).call(this);
