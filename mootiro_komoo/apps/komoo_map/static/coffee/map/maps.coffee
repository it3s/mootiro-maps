define ['map/controls', 'map/maptypes', 'map/providers', 'map/collections', 'map/features'], () ->

    window.komoo ?= {}
    window.komoo.event ?= google.maps.event

    class Map
        featureTypesUrl: '/map_info/feature_types/'

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
            @element = @options.element ? \
                       document.getElementById @options.elementId

            @features = komoo.collections.makeFeatureCollectionPlus map: @

            @components = {}
            @addComponent komoo.controls.makeLocation()

            @initGoogleMap @options.googleMapOptions
            @initFeatureTypes()
            @handleEvents()

        loadGeoJsonFromOptons: ->
            if @options.geojson
                features = @loadGeoJSON @options.geojson, not @options.zoom?
                @centerFeature features?.getAt(0)
            @setZoom @options.zoom

        initGoogleMap: (options = @googleMapDefaultOptions) ->
            @googleMap = new google.maps.Map @element, options
            @handleGoogleMapEvents()
            $(@element).trigger 'initialized', @

        handleGoogleMapEvents: ->
            eventNames = ['click', 'idle']
            eventNames.forEach (eventName) =>
                komoo.event.addListener @googleMap, eventName, (e) =>
                    komoo.event.trigger this, eventName, e

        initFeatureTypes: ->
            @featureTypes ?= {}
            if @options.featureTypes?
                # Get Feature types from options
                @options.featureTypes?.forEach (type) =>
                    @featureTypes[type.type] = type
                @loadGeoJsonFromOptons()
            else
                # Load Feature types via ajax
                $.ajax
                    url: @featureTypesUrl
                    dataType: 'json'
                    success: (data) =>
                        data.forEach (type) =>
                            @featureTypes[type.type] = type
                        @loadGeoJsonFromOptons()

        handleEvents: ->
            komoo.event.addListener this, "drawing_finished", (feature, status) =>
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
            komoo.event.trigger this, 'save_location', center, zoom

        goToSavedLocation: ->
            komoo.event.trigger this, 'goto_saved_location'
            true

        goToUserLocation: ->
            komoo.event.trigger this, 'goto_user_location'

        handleFeatureEvents: (feature) ->
            eventsNames = ['mouseover', 'mouseout', 'mousemove', 'click',
                'dblclick', 'rightclick', 'highlight_changed']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener feature, eventName, (e) =>
                    komoo.event.trigger this, "feature_#{eventName}", e, feature

        goTo: (position, displayMarker = true) ->
            komoo.event.trigger this, 'goto', position, displayMarker

        panTo: (position, displayMarker = false) -> @goTo position, displayMarker

        makeFeature: (geojson, attach = true) ->
            feature = komoo.features.makeFeature geojson, @featureTypes
            if attach then @addFeature feature
            komoo.event.trigger this, 'feature_created', feature
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

            if feature? then @panTo feature.getCenter(), false

        loadGeoJson: (geojson, panTo = false, attach = true) ->
            features = komoo.collections.makeFeatureCollection map: @

            if not geojson?.type? or not geojson.type is 'FeatureCollection'
                return features

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

            komoo.event.trigger this, 'features_loaded', features

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
            komoo.event.trigger this, 'draw_feature', geometryType, feature

        editFeature: (feature = @features.getAt(0), newGeometry) ->
            if newGeometry? and feature.getGeometryType() is komoo.geometries.types.EMPTY
                feature.setGeometry komoo.geometries.makeGeometry geometry:
                    type: newGeometry
                komoo.event.trigger this, 'draw_feature', newGeometry, feature
            else
                komoo.event.trigger this, 'edit_feature', feature

        setMode: (@mode) ->
            komoo.event.trigger this, 'mode_changed', @mode

        selectCenter: (radius, callback) ->
            @selectPerimeter radius, callback

        selectPerimeter: (radius, callback) ->
            komoo.event.trigger this, 'select_perimeter', radius, callback

        ## Delegations

        highlightFeature: ->
            @features.highlightFeature.apply @features, arguments

        getBounds: -> @googleMap.getBounds()

        setZoom: (zoom) -> if zoom? then @googleMap.setZoom zoom
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
            @addComponent komoo.controls.makeSaveLocation()
            @addComponent komoo.controls.makeStreetView()
            @addComponent komoo.controls.makeDrawingManager(), 'drawing'
            @addComponent komoo.controls.makeDrawingControl(), 'drawing'
            @addComponent komoo.controls.makeSupporterBox()
            @addComponent komoo.controls.makePerimeterSelector(), 'perimeter'


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
            @addComponent komoo.controls.makeAutosaveLocation()
            @addComponent komoo.controls.makeStreetView()
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
            @addComponent komoo.controls.makePerimeterSelector(), 'perimeter'


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
