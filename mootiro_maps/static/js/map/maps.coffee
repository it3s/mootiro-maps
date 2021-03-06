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
        projectUrl: '/map_info/project/'

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

            @features = collections.makeFeatureCollectionPlus map: @

            @components = {}
            @setProjectId(@options.projectId)
            @initGoogleMap @options.googleMapOptions
            @initLayers()
            @initFeatureTypes()
            @handleEvents()

            @addComponents [
                'map/controls::Location'
                ['map/controls::LayersBox', 'panel', el: '#map-panel-layers']
                'map/controls::LayersFilter'
            ]

        addControl: (pos, el) ->
            @googleMap.controls[pos].push el

        loadGeoJsonFromOptions: ->
            if @options.geojson
                features_ = @loadGeoJSON @options.geojson, not @options.zoom?
                bounds = features_.getBounds()
                @fitBounds bounds if bounds? and not @projectInfo?
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
            @layers.setMap this
            if @options.layers?
                @loadLayersFromOptions @options
            else
                @loadRemoteLayers(@layersUrl + (@getProjectId() ? ''))

        loadLayer: (data) ->
            layer = @layers.loadLayer data
            @publish 'layer_loaded', layer
            layer

        loadLayers: (data) ->
            _layers = []
            data.forEach (l) => _layers.push @loadLayer l
            _layers

        loadLayersFromOptions: (options) ->
            # Get Layers from options
            @loadLayers options.layers

        loadRemoteLayers: (url) ->
            # Load Layers via ajax
            $.ajax
                url: url
                dataType: 'json'
                success: (data) => @loadLayers data

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

        refresh: ->
            googleMaps.event.trigger @googleMap, 'resize'
            @layers?.refresh()

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

                if attach then feature.setMap @

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

        getCenter: ->
            center = @googleMap.getCenter()
            [center.lat(), center.lng()]

        setMapType: (mapTypeId) -> @googleMap.setMapTypeId mapTypeId
        getMapType: -> @googleMap.getMapTypeId()
        getMapTypeId: -> @googleMap.getMapTypeId()

        fitBounds: (bounds, removeBorder=false) ->
            if not bounds
                if @projectInfo
                    if @projectInfo.custom_bbox?
                        bounds = @projectInfo.custom_bbox ? @projectInfo.bbox
                        removeBorder = true
                    else
                        bounds = @projectInfo.bbox
                else
                    bounds = @features.getBounds()
            if _.isArray bounds  # Accepts bbox array
                sw = new googleMaps.LatLng bounds[1], bounds[0]
                ne = new googleMaps.LatLng bounds[3], bounds[2]
                bounds = new googleMaps.LatLngBounds sw, ne
            if removeBorder
              sw = bounds.getSouthWest()
              ne = bounds.getNorthEast()

              lat1 = sw.lat()
              lng1 = sw.lng()
              lat2 = ne.lat()
              lng2 = ne.lng()

              dx = (lng1 - lng2) / 2.0
              dy = (lat1 - lat2) / 2.0
              cx = (lng1 + lng2) / 2.0
              cy = (lat1 + lat2) / 2.0

              lng1 = cx + dx / 1.4
              lng2 = cx - dx / 1.4
              lat1 = cy + dy / 1.4
              lat2 = cy - dy / 1.4

              sw = new google.maps.LatLng(lat1,lng1)
              ne = new google.maps.LatLng(lat2,lng2)
              bounds = new google.maps.LatLngBounds(sw,ne)
            @googleMap.fitBounds bounds


        getProjectId: -> @projectId
        setProjectId: (@projectId) ->
            @_applyProjectConfig()

        _applyProjectConfig: ->
            return if not @projectId?
            $.ajax
                url: @projectUrl + @projectId
                dataType: 'json'
                success: (data) =>
                    @projectInfo = data
                    console.log "applying project config"
                    @setMapType data.maptype
                    if data.custom_bbox
                        @fitBounds data.custom_bbox, true
                    else
                        @fitBounds data.bbox


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

        constructor: (options) ->
            super options

            if options.projectId?
                @addComponents [
                    ['map/maptypes::CleanMapType', 'mapType']
                ]

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
