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

    getArray: -> @elements


class FeatureCollection extends GenericCollection
    constructor: (options = {}) ->
        super options
        if options.map then @setMap options.map
        options.features?.forEach (feature) => @push(feature)

    push: (feature) ->
        super feature
        feature.setMap(@map)

    setMap: (@map, force) ->
        @forEach (feature) => feature.setMap @map, force
        @handleMapEvents()

    show: ->
        @setMap @map, geometry: true
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
        komoo.event.addListener @map, "zoom_changed", =>


class FeatureCollectionPlus extends FeatureCollection
    constructor: (options = {}) ->
        super options
        @featuresByType = {}

    push: (feature) ->
        super feature
        @featuresByType[feature.getType()] ?= {}
        @featuresByType[feature.getType()]['all'] ?= new FeatureCollection map: @map
        @featuresByType[feature.getType()]['uncategorized'] ?= new FeatureCollection map: @map
        feature.getCategories()?.forEach (category) =>
            @featuresByType[feature.getType()][category.name] ?= new FeatureCollection map: @map
            @featuresByType[feature.getType()][category.name].push(feature)
        if not feature.getCategories()? or feature.getCategories().length is 0
            @featuresByType[feature.getType()]['uncategorized'].push(feature)
        @featuresByType[feature.getType()]['all'].push(feature)

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
            @featuresByType[type]['all']
        else if categories.length is 0
            @featuresByType[type]['uncategorized']
        else
            features = new FeatureCollection map: @map;
            categories.forEach (category) =>
                if @featuresByType[type][category]
                    @featuresByType[type][category].forEach (feature) =>
                        if not strict or not feature.getCategories() or feature.getCategories().length is 1
                            features.push feature
            features



class Layer extends FeatureCollection



window.komoo.collections =
    GenericCollection: GenericCollection
    FeatureCollection: FeatureCollection

    makeFeatureCollection: (options = {}) -> new FeatureCollectionPlus options

