window.komoo ?= {}
window.komoo.event ?= google.maps.event

class Feature
    constructor: (@options = {}) ->
        geometry = @options.geometry
        if @options.geojson
            if @options.geojson.properties
                @setProperties @options.geojson.properties
            geometry ?= komoo.geometries.makeGeometry @options.geojson
        if geometry?
            @setGeometry geometry
            marker = new komoo.geometries.Point
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
    setGeometry: (@geometry) -> @initEvents()

    getGeometryType: -> @geometry?.getGeometryType()

    getMarker: -> @marker
    setMarker: (@marker) ->
        @marker.getOverlay().feature = @
        @initEvents @marker
        @marker

    handleGeometryEvents: ->
        that = @
        komoo.event.addListener @geometry, 'coordinates_changed', (args) ->
            @updateIcon()
            komoo.event.trigger that, 'coordinates_changed', args

    getUrl: ->
        if @properties.type is 'Community'
            dutils.urls.resolve 'view_community',
                community_slug: @properties.community_slug
        else if @properties.type is 'Resource'
            dutils.url.resolve('view_resource',
                resource_id: @properties.id
            ).replace '//', '/'
        else if @properties.type is 'OrganizationBranch'
            dutils.url.resolve('view_organization',
                organization_slug: @properties.organization_slug
            ).replace '//', '/'
        else
            slugname = "#{@properties.type.toLowerCase()}_slug"
            params =
                community_slug: @properties.community_slug
            params[slugname] = @properties[slugname]
            dutils.url.resolve("view_#{@properties.type.toLowerCase()}",
            params).replace('//', '/')

    isHighlighted: -> @highlighted?
    highlight: -> @setHighlight(on)
    setHighlight: (@highlighted) ->
        @updateIcons()
        komoo.event.trigger @, 'highlight_changed', @highlighted

    getIconUrl: (zoom) ->
        zoom ?= if @map then @map.getZoom() else 10
        nearOrFar = if zoom >= @minZoomMarker then "near" else "far"
        highlighted = if @isHighlighted() then "highlighted/" else ""
        categoryOrType =
            if @properties.categories and zoom >= @minZoomMarker
                (@properties.categories[0].name.toLowerCase() +
                if @properties.categories.length > 1 then "-plus" else "")
            else
                @properties.type.toLowerCase()
        "/static/img/#{nearOrFar}/#{highlighted}#{categoryOrType}.png"

    updateIcon: (zoom) -> @setIcon(@getIconUrl(zoom))

    getCategoriesIcons: ->
        for categorie in @properties.categories
            "/static/need_categories/#{category.name.toLowerCase()}.png"

    getProperties: -> @properties
    setProperties: (@properties) ->
    getProperty: (name) -> @properties[name]

    getGeoJsonGeometry: ->
        type: @geometry?.getGeometryType(),
        coordinates: @geometry?.getCoordinates()

    getGeoJsonFeature: ->
        type: 'Feature',
        geometry: @getGeoJsonGeometry(),
        properties: @getProperties()

    setEditable: (@editable) -> @geometry?.setEditable @editable

    showGeometry: -> @geometry?.setMap @map
    hideGeometry: -> @geometry?.setMap null

    showMarker: -> @marker?.setMap @map
    hideMarker: -> @marker?.setMap @map

    getMap: -> @map
    setMap: (@map, force = geometry: false, marker: false) ->
        if @properties.alwaysVisible is on
            force =
                geometry: true,
                marker: false
        zoom = if @map? then @map.getZoom() else 0
        @marker?.setMap(if (zoom <= @maxZoomMarker and zoom >= @minZoomMarker) or force.marker then @map else null)
        @geometry?.setMap(if (zoom <= @maxZoomGeometry and zoom >= @minZoomGeometry) or force.geometry then @map else null)

    getBounds: -> @geometry?.getBounds()

    removeFromMap: ->
        @marker?.setMap(null)
        @setMap(null)

    setVisible: (@visible) ->
        @marker?.setVisible @visible
        @geometry?.setVisible @visible

    getCenter: -> @geometry?.getCenter()

    setOptions: (options) -> @geometry?.setOptions(options)

    getIcon: -> @geometry?.getIcon()
    setIcon: (icon) ->
        @marker?.setIcon icon
        @geometry?.setIcon icon


window.komoo.features =
    Feature: Feature
    makeFeature: (geojson) ->
        new komoo.features.Feature
            geojson: geojson
