define (require) ->
    'use strict'

    #
    # TODO: Integrate the layer system with providers
    #

    Collections = require './collections'

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
            not obj.getProperty(expr.child, obj)
        else if operator is 'or'
            eval_expr(expr.left, obj) or eval_expr(expr.right, obj)
        else if operator is 'and'
            eval_expr(expr.left, obj) and eval_expr(expr.right, obj)

    window.ee = eval_expr

    class Layer
        constructor: (@options = {}) ->
            @cache = new Collections.FeatureCollection()
            @setName @options.name
            @setRule @options.rule
            @setMap @options.map
            @setCollection @options.collection

        getName: -> @name
        setName: (@name) -> this

        getCollection: -> @collection
        setCollection: (@collection) ->
            @cache.clear()
            # We are lazy. Just populate the cache when needed.
            this

        getRule: -> @rule
        setRule: (@rule) -> this

        setMap: (@map) -> @cache.setMap? @map

        show: -> @getFeatures().show()
        hide: -> @getFeatures().hide()

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


    layers =
        Layer: Layer


    return layers
