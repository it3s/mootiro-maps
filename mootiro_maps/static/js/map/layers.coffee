define (require) ->
    'use strict'

    #
    # TODO: Integrate the layer system with providers
    #

    collections = require './collections'

    eval_expr = (expr, obj) ->
        return false if not expr? or not obj?
        operator = expr.operator
        if operator in ['==', 'is', 'equal', 'equals']
            obj.getProperty(expr.property) is expr.value
        else if operator in ['!=', 'isnt', 'not equal', 'not equals', 'different']
            not obj.getProperty(expr.property) is expr.value
        else if operator is 'in'
            obj.getProperty(expr.property) in expr.value
        else if operator in ['contains', 'has'] and Object.prototype.toString.call(expr.value) is '[object Array]'
            res = true
            for v in expr.value
                res = res and v in obj.getProperty(expr.property)
            res
        else if operator in ['contains', 'has']
            expr.value in obj.getProperty(expr.property)
        else if operator in ['!', 'not']
            not eval_expr(expr.child, obj)
        else if operator is 'or'
            eval_expr(expr.left, obj) or eval_expr(expr.right, obj)
        else if operator is 'and'
            eval_expr(expr.left, obj) and eval_expr(expr.right, obj)

    window.ee = eval_expr


    class Layers extends collections.GenericCollection
        addLayer: (layer) ->
            @push layer if not @getLayer layer.getName()
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


    class Layer
        constructor: (@options = {}) ->
            @cache = new collections.FeatureCollection()
            @visible = @options.visible ? on
            @icon = @options.icon?[0] ? ''
            @iconOff = @options.icon?[1] ? ''
            @id = @options.id ? @options.name
            @setPosition @options.position
            @setName @options.name
            @setRule @options.rule
            @setMap @options.map
            @setCollection @options.collection

        getPosition: -> @position
        setPosition: (@position) -> this

        getId: -> @id

        getName: -> @name
        setName: (@name) -> this

        getCollection: -> @collection
        setCollection: (@collection) ->
            @cache.clear()
            # We are lazy. Just populate the cache when needed.
            this

        getRule: -> @rule
        setRule: (@rule) ->
            @cache.clear()
            this

        getIconUrl: -> "/static/" + (if @visible then @icon else @iconOff)

        setMap: (@map) -> @cache.setMap? @map

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

        getFeatures: () ->
            if @cache.isEmpty()
                @updateCache()
            @cache

        updateCache: ->
            @cache.clear()
            filtered = @collection.filter @match, this
            filtered.forEach (feature) => @cache.push feature
            this


    layers =
        Layers: Layers
        Layer: Layer


    return layers
