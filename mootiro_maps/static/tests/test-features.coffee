require ['map/features'], (features) ->

  test 'Basic requirements', =>
    expect 3
    ok Function.call, 'Function.call()'
    ok Object.create, 'Object.create()'
    ok google.maps, 'Google maps API'


  test 'Get geoJson geometry from feature', =>
    expect 1
    coordinates = [1, 2]
    point =
      getGeometryType: -> 'Point'
      getCoordinates: -> coordinates
      getGeoJson: ->
        type: @getGeometryType()
        coordinates: @getCoordinates()

    feature = new features.Feature()
    geometry = {'type': 'Point', 'coordinates': coordinates}
    feature.setGeometry point
    deepEqual feature.getGeoJsonGeometry(), geometry,
        'Should return the geometry containing the coordinates it received'

