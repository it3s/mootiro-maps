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

        @geocoder = new google.maps.Geocoder()

        @initGoogleMap @options.googleMapOptions
        @initFeatureTypes()
        @handleEvents()

    loadGeoJsonFromOptons: ->
        if @options.geojson
            @loadGeoJSON @options.geojson, true

    initGoogleMap: (options = @googleMapDefaultOptions) ->
        @googleMap = new google.maps.Map @element, options
        $(@element).trigger 'initialized', @

    initFeatureTypes: ->
        @featureTypes ?= {}
        if @options.featureTypes?
            # Get Feature types from options
            @options.featureTypes?.forEach (type) =>
                @featureTypes[type.type] = type
            @loadGeoJsonFromOptons()
        else
            # Load Feature types via ajax
            $.ajax url: '/map_info/feature_types/', dataType: 'json', success: (data) =>
                data.forEach (type) =>
                    @featureTypes[type.type] = type
                @loadGeoJsonFromOptons()

    handleEvents: ->
        komoo.event.addListener @, "drawing_finished", (feature, status) =>
            if status is false
                @revertFeature feature
            else if not feature.getProperty("id")?
                @addFeature feature

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

    getComponentsStatus: (type) ->
        status = []
        @components[type]?.forEach (component) =>
            if component.enabled is on
                status.push('enabled')
        if 'enabled' in status
            'enabled'
        else
            'disabled'

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

    goTo: (position, displayMarker = true) ->
        _go = (latLng) =>
            if latLng
                @googleMap.panTo latLng
                if not @searchMarker
                    @searchMarker = new google.maps.Marker()
                    @searchMarker.setMap this.googleMap

                if displayMarker then @searchMarker.setPosition latLng

        if typeof position is "string"  # Got an address
            request = {
                address: position
                region: this.region
            }
            @geocoder.geocode request, (result, status_) =>
                if status_ is google.maps.GeocoderStatus.OK
                    first_result = result[0]
                    latLng = first_result.geometry.location
                    _go latLng
        else
            if position instanceof Array
                latLng = new google.maps.LatLng position[0], position[1]
            else
                latLng = position
            _go latLng

    panTo: (position, displayMarker = false) -> @goTo position, displayMarker

    makeFeature: (geojson, attach = true) ->
        feature = komoo.features.makeFeature geojson, @featureTypes
        if attach then @addFeature feature
        komoo.event.trigger @, 'feature_created', feature
        feature

    addFeature: (feature) =>
        @handleFeatureEvents feature
        @features.push feature

    revertFeature: (feature) ->
        if feature.getProperty("id")?
            # TODO: set the original geometry
        else
            feature.setMap null

    getFeatures: -> @features

    getFeaturesByType: (type, categories, strict) ->
        @features.getByType type, categories, strict

    showFeaturesByType: (type, categories, strict) ->
        @getFeaturesByType(type, categories, strict)?.show()

    hideFeaturesByType: (type, categories, strict) ->
        @getFeaturesByType(type, categories, strict)?.hide()

    showFeatures: (features = @features) -> features.show()

    hideFeatures: (features = @features) -> features.hide()

    centerFeature: (type, id) ->
        feature =
            if type instanceof komoo.features.Feature
                type
            else
                @features.getById type, id

        @panTo feature.getCenter(), false

    loadGeoJson: (geojson, panTo = false, attach = true) ->
        if not geojson?.type? or not geojson.type is 'FeatureCollection'
            return []

        features = komoo.collections.makeFeatureCollection map: @

        geojson.features?.forEach (geojsonFeature) =>
            # Try to get the instance already created
            feature = @features.getById geojsonFeature.properties.type,
                geojsonFeature.properties.id
            # Otherwise create it
            feature ?= @makeFeature geojsonFeature, attach
            features.push feature

            if attach then feature.setMap @

        if panTo and features.getAt(0)?.getBounds()
            @googleMap.fitBounds features.getAt(0).getBounds()

        features

    loadGeoJSON: (geojson, panTo, attach) ->
        @loadGeoJson(geojson, panTo, attach)

    getGeoJson: (options = {}) ->
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

    getGeoJSON: (options) -> @getGeoJson options

    drawNewFeature: (geometryType, featureType) ->
        feature = @makeFeature
            type: 'Feature'
            geometry:
                type: geometryType
            properties:
                name: "New #{featureType}"
                type: featureType
        komoo.event.trigger @, 'draw_feature', geometryType, feature

    editFeature: (feature = @features.getAt 0) ->
        komoo.event.trigger @, 'edit_feature', feature

    setMode: (@mode) ->
        komoo.event.trigger @, 'mode_changed', @mode

    ## Delegations

    getBounds: -> @googleMap.getBounds()

    getZoom: -> @googleMap.getZoom()


class UserEditor extends Map
    constructor: (options) ->
        super options

        @addComponent komoo.maptypes.makeCleanMapType(), 'mapType'
        @addComponent komoo.controls.makeDrawingManager(), 'drawing'


class Editor extends Map
    constructor: (options) ->
        super options

        @addComponent komoo.maptypes.makeCleanMapType(), 'mapType'
        @addComponent komoo.controls.makeDrawingManager(), 'drawing'
        @addComponent komoo.controls.makeDrawingControl(), 'drawing'
        @addComponent komoo.controls.makeSupporterBox()


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

        @addComponent komoo.controls.makeDrawingManager(), 'drawing'
        @addComponent komoo.controls.makeDrawingControl(), 'drawing'


window.komoo.maps =
    Map: Map
    Preview: Preview
    AjaxMap: AjaxMap

    makeMap: (options = {}) ->
        type = options.type ? 'map'

        if type is 'main'
            new AjaxEditor options
        else if type is 'editor'
            new Editor options
        else if type is 'view'
            new AjaxMap options
        else if type is 'preview'
            new Preview options
        else if type is 'userEditor'
            new UserEditor options
