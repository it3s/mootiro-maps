define (require) ->
    'use strict'

    Collections = require './collections'

    class Layer
        constructor: (@options = {}) ->
            @cache = new Collections.FeatureCollection()
            @setName @options.name
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
            # TODO: Create a real rule
            feature.getType() is @getName()

        getFeatures: () ->
            if @cache.isEmpty
                @updateCache()
            @cache

        updateCache: ->
            @cache.clear()
            filtered = @collection.filter @match, this
            filtered.forEach (feature) => @cache.push feature


    layers =
        Layer: Layer


    return layers
