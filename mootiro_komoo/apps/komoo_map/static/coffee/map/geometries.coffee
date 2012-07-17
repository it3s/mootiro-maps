window.komoo ?= {}
window.komoo.event ?= google.maps.event

EMPTY = 'Empty'
POINT = 'Point'
MULTIPOINT = 'MultiPoint'
POLYGON = 'Polygon'
POLYLINE = 'LineString'
MULTIPOLYLINE = 'MultiLineString'

defaults =
    BACKGROUND_COLOR: '#000'
    BACKGROUND_OPACITY: 0.6
    BORDER_COLOR: '#000'
    BORDER_OPACITY: 0.6
    BORDER_SIZE: 1.5
    BORDER_SIZE_HOVER: 2.5
    ZINDEX: 1


class Geometry
    constructor: (@options = {}) ->
        @setFeature @options.feature
        @initOverlay @options

    initOverlay: (options) -> throw "Not Implemented"

    getCoordinates: -> throw "Not Implemented"
    setCoordinates: (coords) -> komoo.event.trigger @, 'coordinates_changed'

    setEditable: (flag) -> throw "Not Implemented"

    initEvents: (object = @overlay) ->
        if not object
            return

        that = @
        eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
            'mouseout', 'mouseover', 'mouseup', 'rightclick']
        eventsNames.forEach (eventName) ->
            komoo.event.addListener object, eventName, (e, args) ->
                komoo.event.trigger that, eventName, e, args

    calculateBounds: ->
        n = s = w = e = null
        getBounds = (pos) ->
            n ?= (s ?= pos[0])
            w ?= (e ?= pos[1])

            n = Math.max pos[0], n
            s = Math.min pos[0], s
            w = Math.min pos[1], w
            e = Math.max pos[1], e
            [[s, w], [n, e]]
        coordinates = @getCoordinates()
        geometryType = @getGeometryType()
        if geometryType isnt POLYGON and geometryType isnt MULTIPOLYLINE
            coordinates = [coordinates]
        for path in coordinates
            for position in path
                bounds = getBounds position
        if bounds?
            @bounds = new google.maps.LatLngBounds \
                @getLatLngFromArray(bounds[0]), @getLatLngFromArray(bounds[1])
        @bounds

    getBounds: -> if @bounds? then @bounds else @calculateBounds()

    getCenter: ->
        if not @overlay
            []
        else
            @getArrayFromLatLng(@overlay.getCenter?() or \
                @getBounds()?.getCenter() or @overlay.getPosition?())

    getOverlay: -> @overlay
    setOverlay: (@overlay) -> @initEvents()

    getFeature: -> @feature
    setFeature: (@feature) ->

    getGeometryType: -> @geometryType

    getDefaultZIndex: -> @feature?.getDefaultZIndex() or defaults.ZINDEX

    getLatLngFromArray: (pos) ->
        if pos? then new google.maps.LatLng pos[0], pos[1] else null

    getArrayFromLatLng: (latLng) ->
        if latLng then [latLng.lat(), latLng.lng()] else []

    getLatLngArrayFromArray: (positions) ->
        @getLatLngFromArray pos for pos in positions

    getArrayFromLatLngArray: (latLngs) ->
        if latLngs then @getArrayFromLatLng(latLng) for latLng in latLngs else []

    getMap: -> @map
    setMap: (@map) ->
        @overlay?.setMap(if @map and @map.googleMap then @map.googleMap else @map)

    getVisible: -> @overlay?.getVisible()
    setVisible: (flag) -> @overlay?.setVisible flag

    setOptions: (@options) -> @overlay?.setOptions(@options)

    getIcon: -> @overlay?.getIcon?()
    setIcon: (icon) -> @overlay?.setIcon?(icon)

    getGeoJson: ->
        type: @getGeometryType(),
        coordinates: @getCoordinates()


class Empty extends Geometry
    geometryType: EMPTY

    initOverlay: (@options = {}) -> true

    getCoordinates: -> []
    setEditable: (flag) -> true

    getGeoJson: -> null


class Point extends Geometry
    geometryType: POINT

    initOverlay: (options) ->
        @setOverlay new google.maps.Marker
            clickable: options.clickable or on
            zIndex: options.zIndex or @getDefaultZIndex()

    initEvents: (object = @overlay) ->
        super object
        that = @
        eventsNames = ['animation_changed', 'clickable_changed',
            'cursor_changed', 'drag', 'dragend', 'daggable_changed',
            'dragstart', 'flat_changed', 'icon_changed', 'position_changed',
            'shadow_changed', 'shape_changed', 'title_changed',
            'visible_changed', 'zindex_changed']
        eventsNames.forEach (eventName) ->
            komoo.event.addListener object, eventName, (e, args) ->
                komoo.event.trigger that, eventName, e, args

    getCoordinates: -> @getArrayFromLatLng @overlay.getPosition()
    setCoordinates: (coords) ->
        @bounds = null
        @overlay.setPosition @getLatLngFromArray coords
        super coords

    setEditable: (flag) -> @overlay.setDraggable flag

    getPosition: -> @overlay.getPosition()
    setPosition: (pos) ->
        @overlay.setPosition(if pos instanceof Array then @getLatLngFromArray pos else pos)

class MultiPoint extends Geometry
    geometryType: MULTIPOINT

    initOverlay: (options) ->
        @setOverlay new MultiMarker
            clickable: options.clickable or on
            zIndex: options.zIndex or @getDefaultZIndex()

    getPoints: -> @overlay.getMarkers().getArray()
    setPoints: (points) -> @overlay.addMarkers points

    guaranteePoints: (len) ->
        points = @overlay.getMarkers()
        if points.length >= len
            points.pop() for i in [0.. points.length - len - 1]
        else
            @overlay.addMarker(new google.maps.Marker @options) for i in [0..len - points.length - 1]

    getCoordinates: -> @getArrayFromLatLng(point.getPosition()) for point in @getPoints()
    setCoordinates: (coords) ->
        if not (coords[0] instanceof Array)
            coords = [coords]
        @guaranteePoints coords.length
        @bounds = null
        point.setPosition(@getLatLngFromArray coords[i]) for point, i in @getPoints()
        super coords

    setEditable: (flag) -> @overlay.setDraggable flag

    getPositions: -> point.getPosition() for point in @getPoints()
    setPositions: (positions) -> @overlay.setPositions(positions)

    getMarkers: -> @overlay.getMarkers()
    addMarkers: (markers) -> @overlay.addMarkers(markers)
    addMarker: (marker) -> @overlay.addMarker(marker)


class LineString extends Geometry
    geometryType: POLYLINE

    initOverlay: (options) ->
        @setOverlay new google.maps.Polyline
            clickable: options.clickable or on
            zIndex: options.zIndex or @getDefaultZIndex()
            strockeColor: options.strokeColor or  @getBorderColor()
            strockOpacity: options.strokeOpacity or @getBorderOpacity()
            strokeWeight: options.strokeWeight or @getBorderSize()

    getCoordinates: -> @getArrayFromLatLng(latLng) for latLng in @overlay.getPath().getArray()
    setCoordinates: (coords) ->
        @overlay.setPath(@getLatLngFromArray(pos) for pos in coords)

    setEditable: (flag) -> @overlay.setEditable flag

    getBorderColor: ->
        @feature?.getBorderColor() or defaults.BORDER_COLOR
    getBorderOpacity: -> @feature?.getBorderOpacity() or defaults.BORDER_OPACITY
    getBorderSize: -> @feature?.getBorderSize() or defaults.BORDER_SIZE

    getPath: -> @overlay.getPath()
    setPath: (path) -> @overlay.setPath(path)

    addPolyline: (polyline) -> @overlay.addPolyline(polyline)


class MultiLineString extends LineString
    geometryType: MULTIPOLYLINE

    initOverlay: (options) ->
        @setOverlay new MultiPolyline
            clickable: options.clickable or on
            zIndex: options.zIndex or @getDefaultZIndex()
            strockeColor: options.strokeColor or @getBorderColor()
            strockOpacity: options.strokeOpacity or @getBorderOpacity()
            strokeWeight: options.strokeWeight or @getBorderSize()

    guaranteeLines: (len) ->
        lines = @overlay.getPolylines()
        if lines.length >= len
            lines.pop() for i in [0.. lines.length - len - 1]
        else
            lines.push(new google.maps.Polyline @options) for i in [0..len - lines.length - 1]

    getCoordinates: -> @getArrayFromLatLngArray(line.getPath().getArray()) for line in @overlay.getPolylines().getArray()
    setCoordinates: (coords) ->
        if not (coords[0][0] instanceof Array)
            coords = [coords]
        @guaranteeLines coords.length
        @bounds = null
        for line, i in @getLines()
            line.setPath @getLatLngArrayFromArray coords[i]

    getPath: -> @getPaths().getAt(0)
    getPaths: -> @overlay.getPaths()
    setPaths: (paths) -> @overlay.setPaths(paths)

    getLines: -> @overlay.getPolylines().getArray()
    setLines: (lines) -> @overlay.addPolylines(lines)


class Polygon extends LineString
    geometryType: POLYGON

    constructor: (options) ->
        super options
        @handleEvents()

    initOverlay: (options) ->
        @setOverlay new google.maps.Polygon
            clickable: options.clickable or on
            zIndex: options.zIndex or @getDefaultZIndex()
            fillColor: options.fillColor or @getBackgroundColor()
            fillOpacity: options.fillOpacity or  @getBackgroundOpacity()
            strokeColor: options.strokeColor or  @getBorderColor()
            strockOpacity: options.strokeOpacity or @getBorderOpacity()
            strokeWeight: options.strokeWeight or @getBorderSize()

    handleEvents: ->
        that = @
        komoo.event.addListener @, 'mousemove', (e) ->
            that.setOptions strokeWeight: that.getBorderSizeHover()
        komoo.event.addListener @, 'mouseout', (e) ->
            that.setOptions strokeWeight: that.getBorderSize()

    getBackgroundColor: -> @feature?.getBackgroundColor() or defaults.BACKGROUND_COLOR
    getBackgroundOpacity: -> @feature?.getBackgroundOpacity() or defaults.BACKGROUND_OPACITY
    getBorderSizeHover: -> @feature?.getBorderSizeHover() or defaults.BORDER_SIZE_HOVER

    getCoordinates: ->
        coords = []
        for path in @overlay.getPaths().getArray()
            subCoords = @getArrayFromLatLngArray path.getArray()
            # Copy the first point as the last one to close the loop
            if subCoords.length
                subCoords.push(subCoords[0])
            if subCoords.length > 0
                coords.push(subCoords)
        coords
    setCoordinates: (coords) ->
        paths = []
        @bounds = null
        for subCoords in coords
            path = @getLatLngArrayFromArray subCoords
            # Remove the last point that closes the loop.
            # This is not used by google maps.
            path.pop()
            paths.push path
        @setPaths paths

    getPath: -> @getPaths().getAt(0)
    getPaths: -> @overlay.getPaths()
    setPaths: (paths) -> @overlay.setPaths(paths)

window.komoo.geometries =
    Empty: Empty
    Point: Point
    MultiPoint: MultiPoint
    LineString: LineString
    MultiLineString: MultiLineString
    Polygon: Polygon

    defaults: defaults

    makeGeometry: (geojsonFeature, feature) ->
        options = feature: feature
        if not geojsonFeature.geometry?
            return new Empty(options)
        type = geojsonFeature.geometry.type
        coords = geojsonFeature.geometry.coordinates
        if type is 'Point' or type is 'MultiPoint' or type is 'marker'
            geometry = new MultiPoint(options)
        else if type is 'LineString' or type is 'polyline'
            coords = [coords] if coords
            geometry = new MultiLineString(options)
        else if type is 'MultiLineString'
            geometry = new MultiLineString(options)
        else if type is 'Polygon' or type is 'polygon'
            geometry = new Polygon(options)
        if coords
            geometry?.setCoordinates coords
        geometry
