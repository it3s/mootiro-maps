define ['map/geometries'], (geometries) ->
    'use strict'

    window.komoo ?= {}
    window.komoo.event ?= google.maps.event

    class Feature
        displayTooltip: on
        displayInfoWindow: on

        constructor: (@options = {}) ->
            geometry = @options.geometry
            @setFeatureType(@options.featureType)
            if @options.geojson
                if @options.geojson.properties
                    @setProperties @options.geojson.properties
                geometry ?= geometries.makeGeometry @options.geojson, @
            if geometry?
                @setGeometry geometry
                @createMarker()

        createMarker: ->
            marker = new geometries.Point
                visible : true
                clickable : true
            marker.setCoordinates @getCenter()
            @setMarker marker

        initEvents: (object = @geometry) ->
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
        setFeatureType: (@featureType = {
            minZoomPoint: 0
            maxZoomPoint: 10
            minZoomIcon: 10
            maxZoomIcon: 100
            minZoomGeometry: 0
            maxZoomGeometry: 100
        }) ->

        getMarker: -> @marker
        setMarker: (@marker) ->
            @marker.getOverlay().feature = @
            @initEvents @marker
            @marker

        handleGeometryEvents: ->
            komoo.event.addListener @geometry, 'coordinates_changed', (args) =>
                @updateIcon()
                komoo.event.trigger this, 'coordinates_changed', args

        getUrl: ->
            if @properties.type is 'Community'
                dutils.urls.resolve 'view_community',
                    community_slug: @properties.community_slug
            else if @properties.type is 'Resource'
                dutils.url.resolve('view_resource',
                    id: @properties.id
                ).replace '//', '/'
            else if @properties.type is 'OrganizationBranch'
                dutils.url.resolve('view_organization',
                    id: @properties.id
                ).replace '//', '/'
            else
                slugname = "#{@properties.type.toLowerCase()}_slug"
                params =
                    community_slug: @properties.community_slug
                params[slugname] = @properties[slugname]
                dutils.url.resolve("view_#{@properties.type.toLowerCase()}",
                params).replace('//', '/')

        isHighlighted: -> @highlighted
        highlight: -> @setHighlight(on)
        setHighlight: (highlighted, silent = false) ->
            if @highlighted is highlighted then return
            @highlighted = highlighted
            @updateIcon()
            if not silent
                komoo.event.trigger @, 'highlight_changed', @highlighted

        isNew: -> not @getProperty 'id'

        getIconUrl: (zoom) ->
            if @getProperty 'image' then return @getProperty 'image'
            zoom ?= if @map then @map.getZoom() else 10
            nearOrFar = if zoom >= @featureType.minZoomIcon then "near" else "far"
            highlighted = if @isHighlighted() then "highlighted/" else ""
            if (@properties.categories and \
                    @properties.categories[0] and \
                    @properties.categories[0].name and \
                    zoom >= @featureType.minZoomIcon)
                categoryOrType = (@properties.categories[0].name.toLowerCase() +
                    if @properties.categories.length > 1 then "-plus" else "")
            else
                categoryOrType = @properties.type.toLowerCase()
            "/static/img/#{nearOrFar}/#{highlighted}#{categoryOrType}.png".replace ' ', '-'

        updateIcon: (zoom) -> @setIcon(@getIconUrl(zoom))

        getCategoriesIcons: ->
            for categorie in @properties.categories
                "/static/need_categories/#{category.name.toLowerCase()}.png"

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
        hideMarker: -> @marker?.setMap @map

        getMap: -> @map
        setMap: (map, force = geometry: false, point: false, icon: false) ->
            @oldMap = @map
            @map = map
            if @properties.alwaysVisible is on or @editable
                force =
                    geometry: true
                    point: false
                    icon: false
            zoom = if @map? then @map.getZoom() else 0
            @marker?.setMap(
                if force.point or force.icon or \
                    @featureType.minZoomPoint <= zoom <= @featureType.maxZoomPoint or \
                    @featureType.minZoomIcon <= zoom <= @featureType.maxZoomIcon then \
                    @map else null)
            @geometry.setMap(if force.geometry or (zoom <= @featureType.maxZoomGeometry and \
                    zoom >= @featureType.minZoomGeometry) then @map else null)
            @updateIcon()

            if @oldMap is undefined
                @handleMapEvents()

        handleMapEvents: ->
            @map.subscribe 'feature_highlight_changed', (flag, feature) =>
                if feature is this then return
                if @isHighlighted()
                    @setHighlight off, true

        getBounds: -> @geometry.getBounds()

        removeFromMap: ->
            @marker?.setMap(null)
            @setMap(null)

        setVisible: (@visible) ->
            @marker?.setVisible @visible
            @geometry.setVisible @visible

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
