define ['googlemaps'], (googleMaps) ->
    'use strict'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    class GenericCollection
        constructor: (@options = {}) ->
            @elements = []
            @length = 0

        updateLength: -> @length = @elements.length

        clear: ->
            @elements = []
            @updateLength()

        getAt: (index) -> @elements[index]

        push: (element) ->
            @elements.push element
            @updateLength()

        pop: ->
            element = @elements.pop()
            @updateLength()
            element

        forEach: (callback, thisArg) ->
            @elements.forEach callback, thisArg

        getArray: -> @elements

        slice: (begin, end) ->
            @elements.slice begin, end


    class FeatureCollection extends GenericCollection
        constructor: (options = {}) ->
            super options
            if options.map then @setMap options.map
            options.features?.forEach (feature) => @push(feature)

        push: (feature) ->
            if not feature?
                return
            super feature
            feature.setMap(@map)

        getBounds: ->
            firstFeature = @getAt 0
            if firstFeature and firstFeature.getGeometryType() isnt 'Empty'
                geometry = firstFeature.getGeometry()
                point = geometry.getLatLngFromArray geometry.getCenter()
                @bounds = new googleMaps.LatLngBounds point, point
                @forEach (feature) =>
                    @bounds?.union feature.getBounds() if feature.getGeometryType() isnt 'Empty'
            @bounds

        setMap: (@map, force) ->
            tmpForce = null
            @forEach (feature) =>
                if force?
                    tmpForce =
                        geometry: force?.geometry
                        point: force?.icon
                        icon: force?.icon

                if feature.getType() is 'Community'
                    tmpForce?['point'] = off

                feature?.setMap @map, tmpForce
            @handleMapEvents()

        show: ->
            @setMap @map, geometry: true
            @setVisible on

        hide: -> @setVisible off

        getGeoJson: (options) ->
            options.geometryCollection ?= false

            if options.geometryCollection
                geojson =
                    type: "GeometryCollection"
                    geometries: []
                @forEach (feature) ->
                    geojson.geometries.push feature.getGeometryGeoJson()
            else
                geojson =
                    type: "FeatureCollection"
                    features: []
                @forEach (feature) ->
                    geojson.features.push feature.getGeoJson()
            geojson

        removeAllFromMap: ->
            @forEach (feature) -> feature.removeFromMap()

        setVisible: (flag) ->
            @forEach (feature) -> feature.setVisible flag

        # Is this been used?
        updateFeaturesVisibility: ->
            @forEach (feature) -> feature.seMap feature.getMap()

        handleMapEvents: ->
            komoo.event.addListener @map, "zoom_changed", =>


    class FeatureCollectionPlus extends FeatureCollection
        constructor: (options = {}) ->
            super options
            @featuresByType = {}

        push: (feature) ->
            super feature
            type = feature.getType()
            @featuresByType[type] ?= {}
            @featuresByType[type]['categories'] ?= {}
            @featuresByType[type]['categories']['all'] ?= new FeatureCollection map: @map
            @featuresByType[type]['categories']['uncategorized'] ?= new FeatureCollection map: @map
            feature.getCategories()?.forEach (category) =>
                @featuresByType[type]['categories'][category.name] ?= new FeatureCollection map: @map
                @featuresByType[type]['categories'][category.name].push(feature)
            if not feature.getCategories()? or feature.getCategories().length is 0
                @featuresByType[type]['categories']['uncategorized'].push(feature)
            @featuresByType[type]['categories']['all'].push(feature)
            @featuresByType[type]['ids'] ?= {}
            @featuresByType[type]['ids'][feature.getProperty('id')] = feature

        pop: ->
            # TODO: remove the feature from featuresByType
            super()

        clear: ->
            @featuresByType = {}
            super()

        getByType: (type, categories, strict = false) ->
            if not @featuresByType[type]
                false
            else if not categories
                @featuresByType[type]['categories']['all']
            else if categories.length is 0
                @featuresByType[type]['categories']['uncategorized']
            else
                features = new FeatureCollection map: @map;
                categories.forEach (category) =>
                    if @featuresByType[type]['categories'][category]
                        @featuresByType[type]['categories'][category].forEach (feature) =>
                            if not strict or not feature.getCategories() or feature.getCategories().length is 1
                                features.push feature
                features

        getById: (type, id) ->
            @featuresByType[type]?['ids'][id]

        highlightFeature: (type, id) ->
            feature =
                if typeof type is 'string'
                    @getById type, id
                else
                    type

            if feature.isHighlighted() then return

            @highlighted?.setHighlight off
            feature.highlight()
            @highlighted = feature


    class Layer extends FeatureCollection



    window.komoo.collections =
        GenericCollection: GenericCollection
        FeatureCollection: FeatureCollection
        FeatureCollectionPlus: FeatureCollectionPlus
        makeFeatureCollection: (options = {}) -> new FeatureCollection options
        makeFeatureCollectionPlus: (options = {}) -> new FeatureCollectionPlus options

    return window.komoo.collections
