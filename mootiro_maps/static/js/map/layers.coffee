define (require) ->
    'use strict'

    #
    # TODO: Integrate the layer system with providers
    #

    collections = require './collections'
    _ = require 'underscore'

    static_path = '/static/'

    equal_ops = ['==', 'is', 'equal', 'equals']
    not_equal_ops = ['!=', 'isnt', 'not equal', 'not equals', 'different']
    in_ops = ['in']
    contains_ops = ['contains', 'has']
    not_ops = ['!', 'not']
    or_ops = ['or']
    and_ops = ['and']

    eval_expr = (expr, obj) ->
        return true if not expr? or not expr.operator?
        return false if not obj?
        operator = expr.operator
        objValue = obj.getProperty(expr.property)
        if operator in equal_ops
            objValue is expr.value
        else if operator in not_equal_ops
            not objValue is expr.value
        else if operator in in_ops
            objValue? and objValue in expr.value
        else if operator in contains_ops and Object.prototype.toString.call(expr.value) is '[object Array]'
            res = true
            for v in expr.value
                res = res and objValue? and v in objValue
            res
        else if operator in contains_ops
            objValue and expr.value in objValue
        else if operator in not_ops
            not eval_expr(expr.child, obj)
        else if operator in or_ops
            eval_expr(expr.left, obj) or eval_expr(expr.right, obj)
        else if operator in and_ops
            eval_expr(expr.left, obj) and eval_expr(expr.right, obj)

    window.ee = eval_expr


    class Layers extends collections.GenericCollection
        addLayer: (layer) ->
            @push layer if not @contains layer
            layer.setLayersCollection this
            layer.map?.publish 'layer_added', layer

        getLayer: (id) ->
            layers = @filter (layer) ->
                layer.getId() is id or layer.getName() is id
            layers.first

        showLayer: (name) -> @getLayer(name).show()
        hideLayer: (name) -> @getLayer(name).hide()

        showAll: -> @forEach (layer) -> layer.show()
        hideAll: -> @forEach (layer) -> layer.hide()

        getVisibleLayers: -> @filter (layer) -> layer.visible
        getHiddenLayers: -> @filter (layer) -> not layer.visible

        shouldFeatureBeVisible: (feature) ->
            #console.log 'AAA', feature.getMap()?
            return false if feature.isOutOfBounds()
            return true if @length is 0
            visible = false
            layers = @_getFromCache feature
            layers.forEach (layerId) =>
                layer = @getLayer layerId
                return if not layer.isVisible()
                visible_ = layer.isVisible()
                @_updateFeatureStyle feature, layer if visible_ and (not visible or layer.isImportant())
                visible or= visible_

            # Orphan features should be visible
            visible = true if layers.length is 0

            visible

        setCollection: (@collection) ->
        getCollection: -> @collection ? @map?.getFeatures() ? []

        loadLayer: (data) ->
            layer = new Layer _.extend {
                collection: @getCollection()
                map: @map
            }, data
            @addLayer layer
            layer

        loadLayers: (data) ->
            layers = []
            data.forEach (l) => layers.push @loadLayer l
            layers

        setMap: (@map) ->
            return if not @map
            @reset()
            @handleMapEvents()
            @forEach (layer) -> layer.setMap @map

        handleMapEvents: ->
            @map.subscribe 'feature_added', (feature) =>
                matched = false
                @forEach (layer) =>
                    if layer.match feature
                        @_addToCache feature, layer
                        @_updateFeatureStyle feature, layer if not matched
                        matched = true
                        layer.cache.push feature if not layer.cache.isEmpty()

        reset: ->
            @_resetCache()
            @forEach (layer) -> layer.reset()

        _resetCache: -> @cache = {}

        _addToCache: (feature, layer) ->
            # Cache the relationship between layers and features
            # to boost layers performance
            @cache[feature.uid] ?= []
            @cache[feature.uid].push layer.getId()

        _getFromCache: (feature) ->
            layers = @cache[feature.uid]
            if not layers
                @forEach (layer) =>
                    @_addToCache(feature, layer) if layer.match feature
            return @cache[feature.uid] ? []

        toJSON: ->
            layers = []
            @forEach (layer) ->
                layers.push layer.toJSON()
            layers

        _updateFeatureStyle: (feature, layer) ->
            feature.setBorderColor layer.getStrokeColor()
            feature.setBackgroundColor layer.getFillColor()
            feature.refresh()



    class Layer
        constructor: (@options = {}) ->
            @cache = new collections.FeatureCollection()
            @visible = @options.visible ? on
            @icon = @options.icon?[0] ? ''
            @iconOff = @options.icon?[1] ? ''
            @fillColor = @options.fillColor ? '#c0c0c0'
            @strokeColor = @options.strokeColor ? @fillColor
            @id = '' + (@options.id ? @options.name)
            @important = @options.important ? false
            @setPosition @options.position
            @setName @options.name
            @setRule @options.rule
            @setCollection @options.collection
            @setMap @options.map

        getPosition: -> @position
        setPosition: (@position) -> this

        getId: -> @id

        getName: -> @name
        setName: (@name) -> this

        getFillColor: -> @fillColor
        setFillColor: (@fillColor) -> this

        getStrokeColor: -> @strokeColor
        setStrokeColor: (@strokeColor) -> this

        getCollection: -> @collection
        setCollection: (@collection) ->
            @cache.clear()
            # We are lazy. Populate the cache when needed.
            this

        getLayersCollection: -> @layersCollection
        setLayersCollection: (@layersCollection) ->

        getRule: -> @rule
        setRule: (@rule) ->
            # Clear the cache because the objects associated with this layer
            # may been changed
            @cache.clear()
            this

        getIconUrl: -> @icon and static_path + (if @visible then @icon else @iconOff)

        setMap: (@map) ->
            return if not @map
            @handleMapEvents()
            @cache.setMap? @map
            @setCollection @map.getFeatures() if not @collection?

        handleMapEvents: ->
            @map.subscribe 'feature_added', (feature) =>
                @cache.push feature if not @cache.isEmpty() and  @match feature

        isVisible: -> @visible

        isImportant: -> @important

        show: ->
            @visible = on
            @getFeatures().show()

        hide: ->
            @visible = off
            @getFeatures().hide()

        toggle: ->
            if not @visible then @show() else @hide()
            @visible

        match: (feature) ->
            eval_expr @rule, feature

        getFeatures: ->
            @updateCache() if @cache.isEmpty()
            @cache

        countFeatures: ->
            @getFeatures().length

        reset: -> @cache.clear()

        updateCache: ->
            @cache.clear()
            filtered = @collection.filter @match, this
            filtered.forEach (feature) =>
                @cache.push feature
            this

        toJSON: ->
            "id": @getId()
            "name": @getName()
            "rule": @getRule()
            "position": @getPosition()
            "fillColor": @getFillColor()
            "strokeColor": @getStrokeColor()


    layers =
        Layers: Layers
        Layer: Layer


    return layers
