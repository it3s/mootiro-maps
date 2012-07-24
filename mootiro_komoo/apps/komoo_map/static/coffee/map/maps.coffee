window.komoo ?= {}
window.komoo.event ?= google.maps.event

class SimpleMap
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
        @providers = []
        @mapTypes = []

        @initGoogleMap @options.googleMapOptions
        @initFeatureTypes()
        @initProviders()
        @initControls()
        @handleEvents()

    initGoogleMap: (options = @googleMapDefaultOptions) ->
        @googleMap = new google.maps.Map @element, options

    initFeatureTypes: ->
        @featureTypes ?= {}
        @options.featureTypes?.forEach (type) =>
            @featureTypes[type.type] = type

    initProviders: ->

    initControls: ->

    handleEvents: ->

    addProvider: (provider) ->
        provider.setMap @
        @providers.push provider

    addMapType: (mapType) ->
        mapType.setMap @
        @mapTypes.push mapType

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
            feature ?= komoo.features.makeFeature geojsonFeature,
                @featureTypes
            features.push feature

            @handleFeatureEvents feature

            if attach
                @features.push feature
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


class Editor extends SimpleMap


class AjaxMap extends SimpleMap
    initProviders: ->
        super()
        @addProvider komoo.providers.makeFeatureProvider()


class AjaxEditor extends Editor
    initProviders: ->
        super()
        @addProvider komoo.providers.makeFeatureProvider()


window.komoo.maps =
    SimpleMap: SimpleMap
    AjaxMap: AjaxMap

    makeMap: (options = {}) -> new AjaxMap options
