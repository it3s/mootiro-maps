window.komoo ?= {}
window.komoo.event ?= google.maps.event

class Map
    googleMapDefaultOptions:
        zoom: 12
        center: new google.maps.LatLng(-23.55, -46.65)
        disableDefaultUI: false
        streetViewControl: true
        scaleControl: true
        panControlOptions:
            position: google.maps.ControlPosition.RIGHT_TOP
        zoomControlOptions:
            position: google.maps.ControlPosition.RIGHT_TOP
        scaleControlOptions:
            position: google.maps.ControlPosition.RIGHT_BOTTOM
            style: google.maps.ScaleControlStyle.DEFAULT
        mapTypeControlOptions:
            mapTypeIds: [google.maps.MapTypeId.ROADMAP,
                         google.maps.MapTypeId.HYBRID]
        mapTypeId: google.maps.MapTypeId.HYBRID

    constructor: (@options = {}) ->
        @element = document.getElementById(@options.elementId);

        @features = komoo.collections.makeFeatureCollectionPlus map: @

        @components = {}

        @initGoogleMap @options.googleMapOptions
        @initFeatureTypes()
        @handleEvents()

        if @options.geojson
            @loadGeoJSON @options.geojson, true

    initGoogleMap: (options = @googleMapDefaultOptions) ->
        @googleMap = new google.maps.Map @element, options

    initFeatureTypes: ->
        @featureTypes ?= {}
        @options.featureTypes?.forEach (type) =>
            @featureTypes[type.type] = type

    handleEvents: ->

    addComponent: (component, type = 'generic') ->
        component.setMap @
        @components[type] ?= []
        @components[type].push component
        component.enable?()

    enableComponents: (type) ->
        @components[type]?.forEach (component) =>
            component.enable?()

    disableComponents: (type) ->
        @components[type]?.forEach (component) =>
            component.disable?()

    clear: ->
        @features.removeAllFromMap()
        @features.clear()

    refresh: -> google.maps.event.trigger @googleMap, 'resize'

    saveLocation: (center = @googleMap.getCenter(), zoom = @getZoom()) ->
        komoo.utils.createCookie 'lastLocation', center.toUrlValue(), 90
        komoo.utils.createCookie 'lastZoom', zoom, 90

    goToSavedLocation: ->
        lastLocation = komoo.utils.readCookie 'lastLocation'
        zoom = parseInt komoo.utils.readCookie('lastZoom'), 10
        if lastLocation and zoom
            console?.log 'Getting location from cookie...'
            lastLocation = lastLocation.split ','
            center = new google.maps.LatLng lastLocation[0], lastLocation[1]
            @googleMap.setCenter center
            @googleMap.setZoom zoom
        true
    false

    goToUserLocation: ->
        if clientLocation = google.loader.ClientLocation
            pos = new google.maps.LatLng clientLocation.latitude,
                                         clientLocation.longitude
            @googleMap.setCenter pos
            console?.log 'Getting location from Google...'
        if navigator.geolocation
            navigator.geolocation.getCurrentPosition (position) =>
                pos = new google.maps.LatLng position.coords.latitude,
                                             position.coords.longitude
                @googleMap.setCenter pos
                console?.log 'Getting location from navigator.geolocation...'
            , =>
                console?.log 'User denied access to navigator.geolocation...'


    handleFeatureEvents: (feature) ->
        eventsNames = ['mouseover', 'mouseout', 'mousemove', 'click',
            'dblclick']
        eventsNames.forEach (eventName) =>
            komoo.event.addListener feature, eventName, (e) =>
                komoo.event.trigger @, "feature_#{eventName}", e, feature

    makeFeature: (geojson) ->
        feature = komoo.features.makeFeature geojson, @featureTypes
        @handleFeatureEvents feature
        @features.push feature
        komoo.event.trigger @, 'feature_created', feature
        feature

    getFeatures: -> @features

    getFeaturesByType: (type, categories, strict) ->
        @features.getByType type, categories, strict

    showFeaturesByType: (type, categories, strict) ->
        @getFeaturesByType(type, categories, strict)?.show()

    hideFeaturesByType: (type, categories, strict) ->
        @getFeaturesByType(type, categories, strict)?.hide()

    showFeatures: (features = @features) -> features.show()

    hideFeatures: (features = @features) -> features.hide()

    loadGeoJSON: (geojson, panTo = false, attach = true) ->
        if not geojson?.type?
            return []
        if not geojson.type is 'FeatureCollection'
            return []

        features = komoo.collections.makeFeatureCollection map: @

        geojson.features?.forEach (geojsonFeature) =>
            # Try to get the instance already created
            feature = @features.getById geojsonFeature.properties.type,
                geojsonFeature.properties.id
            # Otherwise create it
            feature ?= @makeFeature geojsonFeature
            features.push feature

            if attach
                feature.setMap @

        if panTo and features.getAt(0)?.getBounds()
            @googleMap.fitBounds features.getAt(0).getBounds()

        features

    getGeoJSON: (options = {}) ->
        options.newOnly ?= false
        options.currentOnly ?= false
        options.geometryCollection ?= false

        list =
            if options.newOnly
                @newFeatures
            else if options.currentOnly
                komoo.collections.makeFeatureCollection
                    map: @map
                    features: [@currentFeature]
            else
                @features

        list.getGeoJson
            geometryCollection: options.geometryCollection

    ## Delegations

    getBounds: -> @googleMap.getBounds()

    getZoom: -> @googleMap.getZoom()


class Editor extends Map


class Preview extends Map
    googleMapDefaultOptions:
        zoom: 12
        center: new google.maps.LatLng(-23.55, -46.65)
        disableDefaultUI: true
        streetViewControl: false
        scaleControl: true
        scaleControlOptions:
            position: google.maps.ControlPosition.RIGHT_BOTTOM
            style: google.maps.ScaleControlStyle.DEFAULT
        mapTypeId: google.maps.MapTypeId.HYBRID


class AjaxMap extends Map
    constructor: (options) ->
        super options

        @addComponent komoo.maptypes.makeCleanMapType(), 'mapType'
        @addComponent komoo.providers.makeFeatureProvider(), 'provider'
        @addComponent komoo.controls.makeTooltip(), 'tooltip'
        @addComponent komoo.controls.makeInfoWindow(), 'infoWindow'
        @addComponent komoo.controls.makeFeatureClusterer featureType: "Community", 'clusterer'
        @addComponent komoo.controls.makeSupporterBox()
        @addComponent komoo.controls.makeLicenseBox()


class AjaxEditor extends AjaxMap
    constructor: (options) ->
        super options

        @addComponent komoo.controls.makeDrawingManager()



window.komoo.maps =
    Map: Map
    Preview: Preview
    AjaxMap: AjaxMap

    makeMain: (options = {}) -> new AjaxEditor options
    makeView: (options = {}) -> new AjaxMap options
    makeEditor: (options = {}) -> new AjaxEditor options
    makePreview: (options = {}) -> new Preview options
