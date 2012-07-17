window.komoo ?= {}
window.komoo.event ?= google.maps.event

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


class FeatureCollection extends GenericCollection
    constructor: (options = {}) ->
        super options
        if options.map
            @setMap options.map
        if options.features
            options.features.forEach (feature) ->
                @push(feature)

    push: (feature) ->
        super feature
        feature.setMap(@map)

    setMap: (@map, opt_force) ->
        @forEach (feature) -> feature.setMap @map, opt_force
        @handleMapEvents()

    show: ->
        @setMap @map, geometries: true
        @setVisible on

    hide: -> @setVisible off

    getGeoJson: ->
        features = []
        geojson =
            type: "FeatureCollection"
            features: features
        @forEach (feature) -> features.push feature.getGeoJson()
        geojson

    removeAllFromMap: ->
        @forEach (feature) -> feature.removeFromMap()

    setVisible: (flag) ->
        @forEach (feature) -> feature.setVisible flag

    # Is this been used?
    updateFeaturesVisibility: ->
        @forEach (feature) -> feature.seMap feature.getMap()

    handleMapEvents: ->
        that = @
        komoo.event.addListener @map, "zoom_changed", ->


class Layer extends FeatureCollection



window.komoo.collections =
    GenericCollection: GenericCollection
    FeatureCollection: FeatureCollection

    makeFeatureCollection: (options = {}) ->
        new FeatureCollection options

