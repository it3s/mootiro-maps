require ['map/geometries'], (geometries) ->

    module 'Map Geometries'

    test 'Basic requirements', ->
        expect 2
        ok Function.call, 'Function.call()'
        ok Object.create, 'Object.create()'


    test 'Get geometry default properties', ->
        expect 6
        simpleGeometry = new geometries.Polygon()
        equal simpleGeometry.getBackgroundColor(),
            geometries.defaults.BACKGROUND_COLOR,
            'Should return the default background color'
        equal simpleGeometry.getBackgroundOpacity(),
            geometries.defaults.BACKGROUND_OPACITY,
            'Should return the default background opacity'
        equal simpleGeometry.getBorderColor(),
            geometries.defaults.BORDER_COLOR,
            'Should return the default border color'
        equal simpleGeometry.getBorderOpacity(),
            geometries.defaults.BORDER_OPACITY,
            'Should return the default border opacity'
        equal simpleGeometry.getBorderSize(),
            geometries.defaults.BORDER_SIZE,
            'Should return the default border size'
        equal simpleGeometry.getDefaultZIndex(),
            geometries.defaults.ZINDEX,
            'Should return the default z-index'


    test 'Get geometry properties from "feature"', ->
        expect 6
        simpleGeometry = new geometries.Polygon()
        fakeFeature =
          getBackgroundColor: -> return '#fff'
          getBackgroundOpacity: -> return 0.5
          getBorderColor: -> return '#ccc'
          getBorderOpacity: -> return 0.8
          getBorderSize: -> return 10
          getDefaultZIndex: -> return 100

        simpleGeometry.setFeature fakeFeature

        equal simpleGeometry.getBackgroundColor(), '#fff',
            'Should return the background color from feature'
        equal simpleGeometry.getBackgroundOpacity(), 0.5,
            'Should return the background opacity from feature'
        equal simpleGeometry.getBorderColor(), '#ccc',
            'Should return the border color from feature'
        equal simpleGeometry.getBorderOpacity(), 0.8,
            'Should return the border opacity from feature'
        equal simpleGeometry.getBorderSize(), 10,
            'Should return the border size from feature'
        equal simpleGeometry.getDefaultZIndex(), 100,
            'Should return the z-index from feature'


    test 'Create point geometry with googles marker object', ->
        expect 3
        simplePoint = new geometries.Point()
        ok simplePoint.overlay, 'Should create googleObject'
        ok geometries.MultiMarker.prototype.isPrototypeOf(
              simplePoint.overlay),
            'object should be a google.maps.Marker object'
        equal simplePoint.getGeometryType(), 'Point',
            'Geometry type should be "Point"'


    test 'Create polyline geometry with googles polyline object', ->
        expect 3
        simplePolyline = new geometries.LineString()
        ok simplePolyline.overlay, 'Should create googleObject'
        ok google.maps.Polyline.prototype.isPrototypeOf(
              simplePolyline.overlay),
            'object should be a google.maps.Polyline object'
        equal simplePolyline.getGeometryType(), 'LineString',
            'Geometry type should be "LineString"'


    test 'Create polygon geometry with googles polygon object', ->
        expect 3
        simplePolygon = new geometries.Polygon()
        ok simplePolygon.overlay, 'Should create googleObject'
        ok google.maps.Polygon.prototype.isPrototypeOf(
              simplePolygon.overlay),
            'object should be a google.maps.Polygon object'
        equal simplePolygon.getGeometryType(), 'Polygon',
            'Geometry type should be "Polygon"'


    test 'Create multipoint geometry with MultiMarker object', ->
        expect 3
        simpleMultiPoint = new geometries.MultiPoint()
        ok simpleMultiPoint.overlay, 'Should create googleObject'
        ok MultiMarker.prototype.isPrototypeOf(simpleMultiPoint.overlay),
            'object should be a MultiMarker object'
        equal simpleMultiPoint.getGeometryType(), 'MultiPoint',
            'Geometry type should be "MultiPoint"'


    test 'Set coordinates to point geometry', ->
        expect 2
        point = new geometries.Point()
        coordinates = [0, 1]
        point.setCoordinates coordinates
        position = point.overlay.getPosition()
        equal position.lat(), coordinates[0]
        equal position.lng(), coordinates[1]


    test 'Get coordinates from point geometry', ->
        expect 1
        point = new geometries.Point()
        coordinates = [[1, 2]]
        point.setCoordinates coordinates
        deepEqual point.getCoordinates(), coordinates,
            'Should return the same coordinates it received'


    test 'Get coordinates from empty point geometry', ->
        expect 1
        point = new geometries.Point()
        deepEqual point.getCoordinates(), [],
            'Should return null'



    test 'Set coordinates to polyline geometry', ->
        expect 10
        polyline = new geometries.LineString()
        coordinates = [[0, 0], [0, 1], [1, 1], [1, 0], [1, 2]]
        polyline.setCoordinates coordinates
        googlePath = polyline.overlay.getPath()
        googlePath.forEach (pos, i) ->
          equal pos.lat(), coordinates[i][0]
          equal pos.lng(), coordinates[i][1]



    test 'Get coordinates from polyline geometry', ->
        expect 1
        polyline = new geometries.LineString()
        coordinates = [[0, 0], [0, 1], [1, 1], [1, 0], [1, 2]]
        polyline.setCoordinates coordinates
        deepEqual polyline.getCoordinates(), coordinates,
            'Should return the same coordinates it received'


    test 'Get coordinates from empty polyline geometry', ->
        expect 1
        polyline = new geometries.LineString()
        deepEqual polyline.getCoordinates(), [],
            'Should return an empty array'


    test 'Set coordinates to polygon geometry', ->
        expect 16
        polygon = new geometries.Polygon()
        coordinates = [
          [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
          [[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]]]
        polygon.setCoordinates coordinates
        googlePaths = polygon.overlay.getPaths()
        googlePaths.forEach (path, i) ->
          path.forEach (pos, j) ->
            equal pos.lat(), coordinates[i][j][0]
            equal pos.lng(), coordinates[i][j][1]




    test 'Get coordinates from polygon geometry', ->
        expect 1
        polygon = new geometries.Polygon()
        coordinates = [
          [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
          [[2, 2], [2, 3], [3, 3], [3, 2], [2, 2]]]
        polygon.setCoordinates coordinates
        deepEqual polygon.getCoordinates(), coordinates,
            'Should return the same coordinates it received'


    test 'Get coordinates from empty polygon geometry', ->
        expect 1
        polygon = new geometries.Polygon()
        deepEqual polygon.getCoordinates(), [],
            'Should return an empty array'


    test 'Set coordinates to multpoint geometry', ->
        expect 4
        multiPoint = new geometries.MultiPoint()
        coordinates = [[0,1], [3,4]]
        multiPoint.setCoordinates coordinates
        positions = multiPoint.getPositions()
        equal positions[0].lat(), coordinates[0][0]
        equal positions[0].lng(), coordinates[0][1]
        equal positions[1].lat(), coordinates[1][0]
        equal positions[1].lng(), coordinates[1][1]


    test 'Get coordinates from multipoint geometry', ->
        expect 1
        multiPoint = new geometries.MultiPoint()
        coordinates = [[0, 1], [3, 4]]
        multiPoint.setCoordinates coordinates
        deepEqual multiPoint.getCoordinates(), coordinates,
            'Should return the same coordinates it received'


    test 'Get coordinates from empty multipoint geometry', ->
        expect 1
        multiPoint = new geometries.MultiPoint()
        deepEqual multiPoint.getCoordinates(), [],
            'Should return an empty array'


    test 'Geometry factory', ->
        expect 3
        pointFeature =
          'type': 'Feature'
          'geometry':
            'type': 'Point'
            'coordinates': [1, 2]
          'properties': null
        point = geometries.makeGeometry pointFeature
        ok point instanceof geometries.MultiPoint,
            'Geometry object shoud be an instance of geometries.MultiPoint'

        polylineFeature =
          'type': 'Feature'
          'geometry':
            'type': 'LineString'
            'coordinates': [[0, 0], [1, 1], [1, 2]]
          'properties': null
        polyline = geometries.makeGeometry polylineFeature
        ok polyline instanceof geometries.MultiLineString,
            'Geometry object shoud be an instance of geometries.MultiLineString'

        polygonFeature =
          'type': 'Feature'
          'geometry':
            'type': 'Polygon'
            'coordinates': [[[0, 0], [1, 1], [1, 2], [0, 0]]]
          'properties': null
        polygon = geometries.makeGeometry polygonFeature
        ok polygon instanceof geometries.Polygon,
            'Geometry object shoud be an instance of geometries.Polygon'
