define (require) ->
    'use strict'

    googleMaps = require 'googlemaps'
    common = require './common'
    require './multimarker'
    require './multipolyline'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    EMPTY = common.geometries.types.EMPTY
    POINT = common.geometries.types.POINT
    MULTIPOINT = common.geometries.types.MULTIPOINT
    POLYGON = common.geometries.types.POLYGON
    POLYLINE = common.geometries.types.LINESTRING
    LINESTRING = common.geometries.types.LINESTRING
    MULTIPOLYLINE = common.geometries.types.MULTILINESTRING
    MULTILINESTRING = common.geometries.types.MULTILINESTRING

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
            if not object then return

            eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
                'mouseout', 'mouseover', 'mouseup', 'rightclick']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener object, eventName, (e, args) =>
                    komoo.event.trigger @, eventName, e, args

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
                @bounds = new googleMaps.LatLngBounds \
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
            # FIXME: fix this method when the database coords were fixed.
            if pos? then new googleMaps.LatLng pos[0], pos[1] else null

        getArrayFromLatLng: (latLng) ->
            # FIXME: fix this method when the database coords were fixed.
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

        getIconUrl: (zoom) -> @feature?.getIconUrl zoom

        getGeoJson: ->
            type: @getGeometryType(),
            coordinates: @getCoordinates()


    class Empty extends Geometry
        geometryType: EMPTY

        getOverlayOptions: (options) -> {}

        initOverlay: (@options = {}) -> true

        getCoordinates: -> []
        setEditable: (flag) -> true

        getGeoJson: -> null


    class Point extends Geometry
        geometryType: POINT

        getOverlayOptions: (options = {}) ->
            clickable: options.clickable ? on
            zIndex: options.zIndex ? @getDefaultZIndex()
            icon: options.icon ? @getIconUrl options.zoom

        initOverlay: (options) ->
            @setOverlay new googleMaps.Marker @getOverlayOptions options

        initEvents: (object = @overlay) ->
            super object
            eventsNames = ['animation_changed', 'clickable_changed',
                'cursor_changed', 'drag', 'dragend', 'daggable_changed',
                'dragstart', 'flat_changed', 'icon_changed', 'position_changed',
                'shadow_changed', 'shape_changed', 'title_changed',
                'visible_changed', 'zindex_changed']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener object, eventName, (e, args) =>
                    komoo.event.trigger @, eventName, e, args

        getCoordinates: -> @getArrayFromLatLng @overlay.getPosition()
        setCoordinates: (coords) ->
            @bounds = null
            @overlay.setPosition @getLatLngFromArray coords
            super coords

        setEditable: (flag) -> @overlay.setDraggable flag

        getPosition: -> @overlay.getPosition()
        setPosition: (pos) ->
            @overlay.setPosition(if pos instanceof Array then @getLatLngFromArray pos else pos)

        addMarker: (marker) -> @setOverlay(marker)

    class MultiPoint extends Geometry
        geometryType: MULTIPOINT

        getOverlayOptions: (options = {}) ->
            clickable: options.clickable ? on
            zIndex: options.zIndex ? @getDefaultZIndex()
            icon: options.icon ? @getIconUrl options.zoom

        initOverlay: (options) ->
            @setOverlay new MultiMarker @getOverlayOptions options

        getPoints: -> @overlay.getMarkers().getArray()
        setPoints: (points) -> @overlay.addMarkers points

        guaranteePoints: (len) ->
            points = @overlay.getMarkers()
            if points.length >= len
                points.pop() for i in [0.. points.length - len - 1]
            else
                @overlay.addMarker(new googleMaps.Marker @options) for i in [0..len - points.length - 1]

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


    class SinglePoint extends MultiPoint
        geometryType: POINT

        getGeoJson: ->
            type: MULTIPOINT,
            coordinates: @getCoordinates()


    class LineString extends Geometry
        geometryType: LINESTRING

        constructor: (options) ->
            super options
            @handleEvents()

        getOverlayOptions: (options = {}) ->
            clickable: options.clickable ? on
            zIndex: options.zIndex ? @getDefaultZIndex()
            strokeColor: options.strokeColor ?  @getBorderColor()
            strokOpacity: options.strokeOpacity ? @getBorderOpacity()
            strokeWeight: options.strokeWeight ? @getBorderSize()

        initOverlay: (options) ->
            @setOverlay new googleMaps.Polyline @getOverlayOptions options

        handleEvents: ->
            komoo.event.addListener @, 'mousemove', (e) =>
                @setOptions strokeWeight: @getBorderSizeHover()
            komoo.event.addListener @, 'mouseout', (e) =>
                @setOptions strokeWeight: @getBorderSize()

        getCoordinates: -> @getArrayFromLatLng(latLng) for latLng in @overlay.getPath().getArray()
        setCoordinates: (coords) ->
            @overlay.setPath(@getLatLngFromArray(pos) for pos in coords)

        setEditable: (flag) -> @overlay.setEditable flag

        getBorderColor: ->
            @feature?.getBorderColor() or defaults.BORDER_COLOR
        getBorderOpacity: -> @feature?.getBorderOpacity() or defaults.BORDER_OPACITY
        getBorderSize: -> @feature?.getBorderSize() or defaults.BORDER_SIZE
        getBorderSizeHover: -> @feature?.getBorderSizeHover() or defaults.BORDER_SIZE_HOVER

        getPath: -> @overlay.getPath()
        setPath: (path) -> @overlay.setPath(path)


    class MultiLineString extends LineString
        geometryType: MULTIPOLYLINE

        initOverlay: (options) ->
            @setOverlay new MultiPolyline @getOverlayOptions options

        guaranteeLines: (len) ->
            lines = @overlay.getPolylines()
            if lines.length >= len
                lines.pop() for i in [0.. lines.length - len - 1]
            else
                @overlay.addPolyline(new googleMaps.Polyline @options) for i in [0..len - lines.length - 1]

        getCoordinates: -> @getArrayFromLatLngArray(line.getPath().getArray()) for line in @overlay.getPolylines().getArray()
        setCoordinates: (coords) ->
            if not (coords[0][0] instanceof Array)
                coords = [coords]
            @guaranteeLines coords.length
            @bounds = null
            for line, i in @getLines()
                line.setPath @getLatLngArrayFromArray coords[i]

        getBorderSize: -> super() + 1
        getBorderSizeHover: ->  super() + 1

        getPath: -> @getPaths().getAt(0)
        getPaths: -> @overlay.getPaths()
        setPaths: (paths) -> @overlay.setPaths(paths)

        getLines: -> @overlay.getPolylines().getArray()
        setLines: (lines) -> @overlay.addPolylines(lines)

        addPolyline: (polyline, keep) -> @overlay.addPolyline(polyline, keep)

        getPolylines: -> @overlay.getPolylines()


    class Polygon extends LineString
        geometryType: POLYGON

        getOverlayOptions: (options = {}) ->
            clickable: options.clickable ? on
            zIndex: options.zIndex ? @getDefaultZIndex()
            fillColor: options.fillColor ? @getBackgroundColor()
            fillOpacity: options.fillOpacity ?  @getBackgroundOpacity()
            strokeColor: options.strokeColor ?  @getBorderColor()
            strokeOpacity: options.strokeOpacity ? @getBorderOpacity()
            strokeWeight: options.strokeWeight ? @getBorderSize()

        initOverlay: (options) ->
            @setOverlay new googleMaps.Polygon @getOverlayOptions options

        getBackgroundColor: -> @feature?.getBackgroundColor() or defaults.BACKGROUND_COLOR
        getBackgroundOpacity: -> @feature?.getBackgroundOpacity() or defaults.BACKGROUND_OPACITY

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
        types:
            EMPTY: EMPTY
            POINT: POINT
            MULTIPOINT: MULTIPOINT
            POLYGON: POLYGON
            POLYLINE: POLYLINE
            LINESTRING: LINESTRING
            MULTIPOLYLINE: MULTIPOLYLINE
            MULTILINESTRING: MULTILINESTRING

        MultiMarker: MultiMarker

        Geometry: Geometry
        Empty: Empty
        Point: SinglePoint
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
            if type is 'Point'
                geometry = new SinglePoint(options)
            else if type is 'MultiPoint' or type is 'marker'
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

    return window.komoo.geometries
