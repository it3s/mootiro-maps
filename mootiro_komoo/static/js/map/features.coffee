define (require) ->
    'use strict'

    googleMaps = require 'googlemaps'
    geometries = require './geometries'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    # FIXME: Are these zoom options deprecated?
    defaultFeatureType = {
        minZoomPoint: 0
        maxZoomPoint: 10
        minZoomIcon: 10
        maxZoomIcon: 100
        minZoomGeometry: 0
        maxZoomGeometry: 100
    }

    class Feature
        displayTooltip: on
        displayInfoWindow: on

        constructor: (@options = {}) ->
            # Try to get a `geometry` object from options.
            geometry = @options.geometry
            @setFeatureType(@options.featureType)
            if @options.geojson
                @setProperties @options.geojson.properties if @options.geojson.properties
                # If we didnt got geometry from options but got geojson, create
                # a geometry object.
                geometry ?= geometries.makeGeometry @options.geojson, @
            if geometry?
                @setGeometry geometry
                @createMarker()

        createMarker: ->
            # We dont want another marker to geometries that ar already
            # rendered as a marker. So dont create markers to points and
            # multipoints.
            return if @geometry.getGeometryType() in ['Point', 'MultiPoint']
            # Create the marker for polygons and lines and display it at the
            # element center.
            marker = new geometries.Point
                visible : false
                clickable : true
            marker.setCoordinates @getCenter()
            @setMarker marker

        initEvents: (object = @geometry) ->
            # Create an event proxy from google maps overlay object.
            that = @
            eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
                'mouseout', 'mouseover', 'mouseup', 'rightclick', 'drag',
                'dragend', 'draggable_changed', 'dragstart', 'coordinates_changed']
            eventsNames.forEach (eventName) ->
                komoo.event.addListener object, eventName, (e, args) ->
                    komoo.event.trigger that, eventName, e, args

        getGeometry: -> @geometry
        setGeometry: (@geometry) ->
            @geometry.feature = @
            @initEvents()

        getGeometryType: -> @geometry.getGeometryType()

        getFeatureType: -> @featureType
        setFeatureType: (@featureType = defaultFeatureType) ->

        getMarker: -> @marker
        setMarker: (@marker) ->
            @marker.getOverlay().feature = @
            # Proxy the marker events.
            @initEvents @marker
            @marker

        handleGeometryEvents: ->
            # React to geometry changes.
            komoo.event.addListener @geometry, 'coordinates_changed', (args) =>
                @updateIcon()
                komoo.event.trigger this, 'coordinates_changed', args

        getUrl: ->
            viewName = "view_#{@properties.type.toLowerCase()}"
            dutils.urls.resolve(viewName, id: @properties.id).replace('//', '/')

        isHighlighted: -> @highlighted
        highlight: -> @setHighlight(on)
        setHighlight: (highlighted, silent = false) ->
            return if @highlighted is highlighted
            @highlighted = highlighted
            @updateIcon()
            komoo.event.trigger @, 'highlight_changed', @highlighted if not silent

        isNew: -> not @getProperty 'id'

        getIconUrl: (zoom) ->
            # Verify if the feature instance have a custom icon configurated.
            return @getProperty 'image' if @getProperty 'image'
            # Get the default icon using the feature type, the zoom level and
            # if the feature is or not highlighted.
            zoom ?= if @map then @map.getZoom() else 10
            nearOrFar = if zoom >= @featureType.minZoomIcon then "near" else "far"
            highlighted = if @isHighlighted() then "highlighted/" else ""
            categoryOrType = @properties.type.toLowerCase()
            url = "/static/img/#{nearOrFar}/#{highlighted}#{categoryOrType}.png".replace ' ', '-'
            url

        updateIcon: (zoom) -> @setIcon(@getIconUrl(zoom))

        getCategoriesIcons: ->
            # FIXME: Generalize.
            # Return a list o icons, for each feature category.
            for categorie in @getCategories()
                "/static/img/need_categories/#{category.name.toLowerCase()}.png"

        getProperties: -> @properties
        setProperties: (@properties) ->
        getProperty: (name) -> @properties[name]
        setProperty: (name, value) -> @properties[name] = value

        getType: -> @getProperty('type')
        getCategories: -> @getProperty('categories') ? []

        getGeometryGeoJson: -> @geometry.getGeoJson()

        getGeometryCollectionGeoJson: ->
            type: "GeometryCollection"
            geometries: [@getGeometryGeoJson()]

        getGeoJsonGeometry: -> @getGeometryGeoJson()

        getGeoJson: ->
            type: 'Feature',
            geometry: @getGeometryGeoJson()
            properties: @getProperties()

        getGeoJsonFeature: -> @getGeoJson()

        setEditable: (@editable) -> @geometry.setEditable @editable

        showGeometry: -> @geometry.setMap @map
        hideGeometry: -> @geometry.setMap null

        showMarker: -> @marker?.setMap @map
        hideMarker: ->
            # WTF: I dont remember why the hide method add the marker to map.
            @marker?.setMap @map

        getMap: -> @map
        setMap: (map, force = { geometry: false, point: false, icon: false }) ->
            # FIXME: Is the `force` param deprecated?
            @oldMap = @map
            @map = map if map?
            @marker?.setMap(map)
            @geometry.setMap(map)
            @updateIcon()
            @setVisible on

            # `@oldMap` is undefined only at the first time this method is called.
            @handleMapEvents() if @oldMap is undefined

        handleMapEvents: ->
            @map.subscribe 'feature_highlight_changed', (flag, feature) =>
                # Should be only one feature highlighted, so if another feature
                # is set as highlighted we should remove the highlight state
                # from this one.
                return if feature is this
                @setHighlight off, true if @isHighlighted()

        getBounds: -> @geometry.getBounds()

        removeFromMap: ->
            # TODO: Remove the events listenners
            @marker?.setMap(null)
            @setMap(null)

        setVisible: (@visible) ->
            [visible] = @map?.triggerHooks 'before_feature_setVisible', @visible
            @marker?.setVisible visible
            @geometry.setVisible visible

        getCenter: -> @geometry.getCenter()

        setOptions: (options) -> @geometry.setOptions(options)

        getIcon: -> @geometry.getIcon()
        setIcon: (icon) ->
            @marker?.setIcon icon
            @geometry.setIcon icon

        getBorderSize: -> @featureType.border_size
        getBorderSizeHover: -> @featureType.borderSizeHover
        getBorderColor: -> @featureType.borderColor
        getBorderOpacity: -> @featureType.borderOpacity
        getBackgroundColor: -> @featureType.backgroundColor
        getBackgroundOpacity: -> @featureType.backgroundOpacity
        getDefaultZIndex: -> @featureType.zIndex


    window.komoo.features =
        Feature: Feature
        makeFeature: (geojson, featureTypes) ->
            new komoo.features.Feature
                geojson: geojson
                featureType: featureTypes?[geojson?.properties?.type]

    return window.komoo.features
