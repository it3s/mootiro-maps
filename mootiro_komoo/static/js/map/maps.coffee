define (require) ->
    'use strict'

    googleMaps = require 'googlemaps'
    _ = require 'underscore'
    core = require './core'
    Collections = require './collections'
    Features = require './features'
    geometries = require './geometries'
    require './controls'
    require './maptypes'
    require './providers'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    class Map extends core.Mediator
        featureTypesUrl: '/map_info/feature_types/'

        googleMapDefaultOptions:
            zoom: 12
            center: new googleMaps.LatLng(-23.55, -46.65)
            disableDefaultUI: false
            streetViewControl: true
            scaleControl: true
            panControlOptions:
                position: googleMaps.ControlPosition.RIGHT_TOP
            zoomControlOptions:
                position: googleMaps.ControlPosition.RIGHT_TOP
            scaleControlOptions:
                position: googleMaps.ControlPosition.RIGHT_BOTTOM
                style: googleMaps.ScaleControlStyle.DEFAULT
            mapTypeControlOptions:
                mapTypeIds: [googleMaps.MapTypeId.ROADMAP,
                             googleMaps.MapTypeId.HYBRID]
            mapTypeId: googleMaps.MapTypeId.HYBRID

        constructor: (@options = {}) ->
            super()
            @element = @options.element ? \
                       document.getElementById @options.elementId

            @features = Collections.makeFeatureCollectionPlus map: @

            @components = {}
            @addComponent 'map/controls::Location'

            @initGoogleMap @options.googleMapOptions
            @initFeatureTypes()
            @handleEvents()

        addControl: (pos, el) ->
            @googleMap.controls[pos].push el

        loadGeoJsonFromOptions: ->
            if @options.geojson
                features = @loadGeoJSON @options.geojson, not @options.zoom?
                bounds = features.getBounds()
                @fitBounds bounds if bounds?
                features?.setMap this, geometry: on, icon: on
                @publish 'set_zoom', @options.zoom

        initGoogleMap: (options = @googleMapDefaultOptions) ->
            @googleMap = new googleMaps.Map @element, options
            @handleGoogleMapEvents()
            $(@element).trigger 'initialized', @

        handleGoogleMapEvents: ->
            eventNames = ['click', 'idle', 'maptypeid_changed', 'zoom_changed']
            eventNames.forEach (eventName) =>
                komoo.event.addListener @googleMap, eventName, (e) =>
                    @publish eventName, e

        initFeatureTypes: ->
            @featureTypes ?= {}
            if @options.featureTypes?
                # Get Feature types from options
                @options.featureTypes?.forEach (type) =>
                    @featureTypes[type.type] = type
                @loadGeoJsonFromOptions()
            else
                # Load Feature types via ajax
                $.ajax
                    url: @featureTypesUrl
                    dataType: 'json'
                    success: (data) =>
                        data.forEach (type) =>
                            @featureTypes[type.type] = type
                        @loadGeoJsonFromOptions()

        handleEvents: ->
            @subscribe 'features_loaded', (features) =>
                komoo.event.trigger this, 'features_loaded', features

            @subscribe 'close_clicked', =>
                komoo.event.trigger this, 'close_click'

            @subscribe 'drawing_started', (feature) =>
                komoo.event.trigger this, 'drawing_started', feature

            @subscribe 'drawing_finished', (feature, status) =>
                komoo.event.trigger this, 'drawing_finished', feature, status
                if status is false
                    @revertFeature feature
                else if not feature.getProperty("id")?
                    @addFeature feature

            @subscribe 'set_location', (location) =>
                location = location.split ','
                center = new googleMaps.LatLng location[0], location[1]
                @googleMap.setCenter center

            @subscribe 'set_zoom', (zoom) =>
                @setZoom zoom

            @subscribe 'idle', (zoom) =>
              @getFeatures().setVisible true

        addComponent: (component, type = 'generic', opts = {}) ->
            component =
            if _.isString component
                @start component, '', opts
            else
                @start component
            return @data.when(component).done () =>
                for instance in arguments
                    instance.setMap @
                    @components[type] ?= []
                    @components[type].push instance
                    instance.enable?()

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

        refresh: -> googleMaps.event.trigger @googleMap, 'resize'

        saveLocation: (center = @googleMap.getCenter(), zoom = @getZoom()) ->
            @publish 'save_location', center, zoom

        goToSavedLocation: ->
            @publish 'goto_saved_location'
            true

        goToUserLocation: ->
            @publish 'goto_user_location'

        handleFeatureEvents: (feature) ->
            eventsNames = ['mouseover', 'mouseout', 'mousemove', 'click',
                'dblclick', 'rightclick', 'highlight_changed']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener feature, eventName, (e) =>
                    @publish "feature_#{eventName}", e, feature

        goTo: (position, displayMarker = true) ->
            @publish 'goto', position, displayMarker

        panTo: (position, displayMarker = false) ->
            @goTo position, displayMarker

        makeFeature: (geojson, attach = true) ->
            feature = Features.makeFeature geojson, @featureTypes
            if attach then @addFeature feature
            @publish 'feature_created', feature
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
                if type instanceof Features.Feature
                    type
                else
                    @features.getById type, id

            @panTo feature?.getCenter(), false

        loadGeoJson: (geojson, panTo = false, attach = true, silent = false) ->
            features = Collections.makeFeatureCollection map: @

            if not geojson?.type? or not geojson.type is 'FeatureCollection'
                return features

            geojson.features?.forEach (geojsonFeature) =>
                # Try to get the instance already created
                feature = @features.getById geojsonFeature.properties.type,
                    geojsonFeature.properties.id
                # Otherwise create it
                feature ?= @makeFeature geojsonFeature, attach
                features.push feature
                feature.setVisible true

                #if attach then feature.setMap @

            @fitBounds() if panTo and features.getBounds()?
            @publish 'features_loaded', features if not silent

            features

        loadGeoJSON: (geojson, panTo, attach, silent) ->
            @loadGeoJson(geojson, panTo, attach, silent)

        getGeoJson: (options = {}) ->
            options.newOnly ?= false
            options.currentOnly ?= false
            options.geometryCollection ?= false

            list =
                if options.newOnly
                    @newFeatures
                else if options.currentOnly
                    Collections.makeFeatureCollection
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
            @publish 'draw_feature', geometryType, feature

        editFeature: (feature = @features.getAt(0), newGeometry) ->
            if newGeometry? and feature.getGeometryType() is geometries.types.EMPTY
                feature.setGeometry geometries.makeGeometry geometry:
                    type: newGeometry
                @publish 'draw_feature', newGeometry, feature
            else
                @publish 'edit_feature', feature

        setMode: (@mode) ->
            @publish 'mode_changed', @mode

        selectCenter: (radius, callback) ->
            @selectPerimeter radius, callback

        selectPerimeter: (radius, callback) ->
            @publish 'select_perimeter', radius, callback

        ## Delegations

        highlightFeature: ->
            @centerFeature.apply this, arguments
            @features.highlightFeature.apply @features, arguments

        getBounds: -> @googleMap.getBounds()

        setZoom: (zoom) -> if zoom? then @googleMap.setZoom zoom
        getZoom: -> @googleMap.getZoom()

        fitBounds: (bounds = @features.getBounds()) ->
            @googleMap.fitBounds bounds

        getMapTypeId: ->
            @googleMap.getMapTypeId()


    class UserEditor extends Map
        constructor: (options) ->
            super options

            @addComponent 'map/controls::AutosaveMapType'
            @addComponent 'map/maptypes::CleanMapType', 'mapType'
            @addComponent 'map/controls::DrawingManager', 'drawing'
            @addComponent 'map/controls::SearchBox'


    class Editor extends Map
        constructor: (options) ->
            super options

            @addComponent 'map/controls::AutosaveMapType'
            @addComponent 'map/maptypes::CleanMapType'
            @addComponent 'map/controls::SaveLocation'
            @addComponent 'map/controls::StreetView'
            @addComponent 'map/controls::DrawingManager'
            @addComponent 'map/controls::DrawingControl'
            @addComponent 'map/controls::GeometrySelector'
            @addComponent 'map/controls::SupporterBox'
            @addComponent 'map/controls::PerimeterSelector'
            @addComponent 'map/controls::SearchBox'


    class Preview extends Map
        googleMapDefaultOptions:
            zoom: 12
            center: new googleMaps.LatLng(-23.55, -46.65)
            disableDefaultUI: true
            streetViewControl: false
            scaleControl: true
            scaleControlOptions:
                position: googleMaps.ControlPosition.RIGHT_BOTTOM
                style: googleMaps.ScaleControlStyle.DEFAULT
            mapTypeId: googleMaps.MapTypeId.HYBRID


    class StaticMap extends Map
        constructor: (options) ->
            super options

            @addComponent 'map/controls::AutosaveMapType'
            @addComponent 'map/maptypes::CleanMapType', 'mapType'
            @addComponent 'map/controls::AutosaveLocation'
            @addComponent 'map/controls::StreetView'
            @addComponent 'map/controls::Tooltip', 'tooltip'
            @addComponent 'map/controls::InfoWindow', 'infoWindow'
            @addComponent 'map/controls::SupporterBox'
            @addComponent 'map/controls::LicenseBox'
            @addComponent 'map/controls::SearchBox'
            @addComponent 'map/controls::FeatureFilter'


    class AjaxMap extends StaticMap
        constructor: (options) ->
            super options

            @addComponent 'map/controls::LoadingBox'
            @addComponent 'map/providers::FeatureProvider', 'provider'
            @addComponent 'map/controls::FeatureClusterer', 'clusterer', {map: this}


    class AjaxEditor extends AjaxMap
        constructor: (options) ->
            super options

            @addComponent 'map/controls::DrawingManager'
            @addComponent 'map/controls::DrawingControl'
            @addComponent 'map/controls::GeometrySelector'
            @addComponent 'map/controls::PerimeterSelector'

            if not @goToSavedLocation()
                @goToUserLocation()


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
            else if type is 'static'
                new StaticMap options
            else if type in ['preview', 'tooltip']
                new Preview options
            else if type is 'userEditor'
                new UserEditor options

    return window.komoo.maps
