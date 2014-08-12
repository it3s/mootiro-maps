define (require) ->
    'use strict'

    googleMaps = require 'googlemaps'
    _ = require 'underscore'
    core = require './core'
    collections = require './collections'
    features = require './features'
    layers = require './layers'
    geometries = require './geometries'
    require './controls'
    require './maptypes'
    require './providers'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    class Map extends core.Mediator
        featureTypesUrl: '/map_info/feature_types/'
        layersUrl: '/map_info/layers/'

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
            mapTypeId: googleMaps.MapTypeId.ROADMAP

        constructor: (@options = {}) ->
            super()
            @element = @options.element ? \
                       document.getElementById @options.elementId

            @features = collections.makeFeatureCollectionPlus map: @

            @components = {}
            @setProjectId(@options.projectId)
            @initGoogleMap @options.googleMapOptions
            @initFeatureTypes()
            @initLayers()
            @handleEvents()

            @addComponents [
                'map/controls::Location'
                ['map/controls::LayersBox', 'panel', el: '#map-panel-layers']
            ]

        addControl: (pos, el) ->
            @googleMap.controls[pos].push el

        loadGeoJsonFromOptions: ->
            if @options.geojson
                features_ = @loadGeoJSON @options.geojson, not @options.zoom?
                bounds = features_.getBounds()
                @fitBounds bounds if bounds?
                features_?.setMap this, geometry: on, icon: on
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

        initLayers: ->
            @layers ?= new layers.Layers
            if @options.layers?
                @loadLayersFromOptions @options
            else
                @loadRemoteLayers @layersUrl

        loadLayer: (data) ->
            layer = new layers.Layer _.extend {
                collection: @getFeatures()
                map: this
            }, data
            @layers.addLayer layer

            @publish 'layer_loaded', layer

        loadLayersFromOptions: (options) ->
            # Get Layers from options
            options.layers.forEach (l) => @loadLayer l

        loadRemoteLayers: (url) ->
            # Load Layers via ajax
            $.ajax
                url: url
                dataType: 'json'
                success: (data) =>
                    data.forEach (l) => @loadLayer l

        getLayers: -> @layers

        getLayer: (name) -> @layers.getLayer name

        showLayer: (layer) ->
            layer = @getLayer layer if _.isString layer
            layer.show()
            @publish 'show_layer', layer

        hideLayer: (layer) ->
            layer = @getLayer layer if _.isString layer
            layer.hide()
            @publish 'hide_layer', layer

        handleEvents: ->
            @subscribe 'features_loaded', (features_) =>
                komoo.event.trigger this, 'features_loaded', features_

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
            component_ =
            if _.isString component
                @start component, opts.el , opts
            else
                @start component
            return @data.when(component_).done () =>
                for instance in arguments
                    instance.setMap @
                    @components[type] ?= []
                    @components[type].push instance
                    instance.enable?()

        addComponents: (components) ->
            components_ = []
            for component in components
                component = [component] if _.isString component
                opts = component[2] ? {}
                opts.type ?= component[1] ? 'generic'
                components_.push
                    component: component[0]
                    el: opts.el,
                    opts: opts
            return @data.when(@start components_).done () =>
                for instance in arguments
                    instance.setMap? @
                    @components[instance.type] ?= []
                    @components[instance.type].push instance
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

        goToUserLocation: -> @publish 'goto_user_location'

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
            feature = features.makeFeature geojson, @featureTypes
            if attach then @addFeature feature
            @publish 'feature_created', feature
            feature

        addFeature: (feature) =>
            @handleFeatureEvents feature
            @features.push feature
            @publish 'feature_added', feature

        revertFeature: (feature) ->
            if feature.getProperty("id")?
                # TODO: set the original geometry
            else
                feature.setMap null

        getFeatures: -> @features

        #getFeaturesByType: (type, categories, strict) ->
        #    @features.getByType type, categories, strict

        #showFeaturesByType: (type, categories, strict) ->
        #    @publish 'show_features_by_type', type, categories, strict
        #    @getFeaturesByType(type, categories, strict)?.show()

        #hideFeaturesByType: (type, categories, strict) ->
        #    @publish 'hide_features_by_type', type, categories, strict
        #    @getFeaturesByType(type, categories, strict)?.hide()

        showFeatures: (features_ = @features) -> features_.show()
        hideFeatures: (features_ = @features) -> features_.hide()

        centerFeature: (type, id) ->
            feature =
                if type instanceof features.Feature
                    type
                else
                    @features.getById type, id

            @panTo feature?.getCenter(), false

        loadGeoJson: (geojson, panTo = false, attach = true, silent = false) ->
            features_ = collections.makeFeatureCollection map: @

            if not geojson?.type? or not geojson.type is 'FeatureCollection'
                return features_

            geojson.features?.forEach (geojsonFeature) =>
                # Try to get the instance already created
                feature = @features.getById geojsonFeature.properties.type,
                    geojsonFeature.properties.id
                # Otherwise create it
                feature ?= @makeFeature geojsonFeature, attach
                features_.push feature
                feature.setVisible true

                #if attach then feature.setMap @

            @fitBounds() if panTo and features_.getBounds()?
            @publish 'features_loaded', features_ if not silent

            features_

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
                    collections.makeFeatureCollection
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

        setMode: (@mode) -> @publish 'mode_changed', @mode

        selectCenter: (radius, callback) ->
            @selectPerimeter radius, callback

        selectPerimeter: (radius, callback) ->
            @publish 'select_perimeter', radius, callback

        ## Delegations

        highlightFeature: ->
            @centerFeature.apply this, arguments
            @features.highlightFeature.apply @features, arguments

        getBounds: -> @googleMap.getBounds()

        getZoom: -> @googleMap.getZoom()
        setZoom: (zoom) -> if zoom? then @googleMap.setZoom zoom

        fitBounds: (bounds = @features.getBounds()) ->
            @googleMap.fitBounds bounds

        getMapTypeId: -> @googleMap.getMapTypeId()

        getProjectId: -> @projectId
        setProjectId: (@projectId) ->


    class UserEditor extends Map
        type: 'editor'

        constructor: (options) ->
            super options

            @addComponents [
                'map/controls::AutosaveMapType'
                ['map/maptypes::CleanMapType', 'mapType']
                ['map/controls::DrawingManager', 'drawing']
                'map/controls::SearchBox'
            ]


    class Editor extends Map
        type: 'view'

        constructor: (options) ->
            super options

            @addComponents [
                'map/controls::AutosaveMapType'
                'map/maptypes::CleanMapType'
                'map/controls::SaveLocation'
                'map/controls::StreetView'
                'map/controls::DrawingManager'
                'map/controls::DrawingControl'
                'map/controls::GeometrySelector'
                #'map/controls::SupporterBox'
                'map/controls::PerimeterSelector'
                'map/controls::SearchBox'
            ]


    class Preview extends Map
        type: 'preview'

        googleMapDefaultOptions:
            zoom: 12
            center: new googleMaps.LatLng(-23.55, -46.65)
            disableDefaultUI: true
            streetViewControl: false
            scaleControl: true
            scaleControlOptions:
                position: googleMaps.ControlPosition.RIGHT_BOTTOM
                style: googleMaps.ScaleControlStyle.DEFAULT
            mapTypeId: googleMaps.MapTypeId.ROADMAP


    class StaticMap extends Map
        type: 'view'

        constructor: (options) ->
            super options

            @addComponents [
                'map/controls::AutosaveMapType'
                ['map/maptypes::CleanMapType', 'mapType']
                'map/controls::AutosaveLocation'
                'map/controls::StreetView'
                ['map/controls::Tooltip', 'tooltip']
                ['map/controls::InfoWindow', 'infoWindow']
                #'map/controls::SupporterBox'
                'map/controls::LicenseBox'
                'map/controls::SearchBox'
            ]


    class AjaxMap extends StaticMap
        type: 'view'

        constructor: (options) ->
            super options

            @addComponents [
                'map/controls::LoadingBox'
                ['map/providers::ZoomFilteredFeatureProvider', 'provider']
                ['map/controls::CommunityClusterer', 'clusterer', {map: this}]
                'map/controls::FeatureZoomFilter'
                'map/controls::LayersFilter'
            ]


    class AjaxEditor extends AjaxMap
        type: 'editor'

        constructor: (options) ->
            super options

            @addComponents [
                'map/controls::DrawingManager'
                'map/controls::DrawingControl'
                'map/controls::GeometrySelector'
                'map/controls::PerimeterSelector'
            ]

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
                new StaticMap options
            else if type is 'static'
                new StaticMap options
            else if type in ['preview', 'tooltip']
                new Preview options
            else if type is 'userEditor'
                new UserEditor options

    return window.komoo.maps
