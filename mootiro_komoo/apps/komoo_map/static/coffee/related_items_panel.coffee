define ['lib/underscore-min', 'lib/backbone-min'], () ->
    $ = jQuery

    window.Feature = Backbone.Model.extend
        iconClass: () ->
            if @properties.type is 'OrganizationBranch'
                modelName = 'Organization'
            else
                modelName = @properties.type
            "icon-#{modelName.toLowerCase()}-big"

        toJSON: (attr) ->
            defaultJSON = Backbone.Model.prototype.toJSON.call this, attr
            _.extend defaultJSON,
                iconClass: @iconClass

        displayOnMap: () ->
            $('#map-canvas').komooMap 'highlight',
                type: @get('properties').type
                id: @get('properties').id


    window.FeatureView = Backbone.View.extend
        tagName: 'li'
        className: 'feature'

        events:
            'mouseover': 'displayOnMap'

        initialize: () ->
            _.bindAll this, 'render', 'displayOnMap'
            @template = _.template $('#feature-template').html()

        render: () ->
            console.log 'rendering model: ', @model.toJSON()
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

        displayOnMap: () ->
            @model.displayOnMap()
            this


    window.Features = Backbone.Collection.extend
        model: Feature


    window.FeaturesView = Backbone.View.extend
        initialize: () ->
            _.bindAll this, 'render'

            @template = _.template $('#features-template').html()
            @collection.bind 'reset', @render

        render: () ->
            @$el.html @template({})
            $features = this.$ '.feature-list'

            collection = @collection
            collection.each (feature) ->
                view = new FeatureView
                    model: feature
                    # collection: collection
                $features.append view.render().$el
            this

    $ ->
        KomooNS ?= {}
        KomooNS.features = geojson.features;

        loadedFeatures = new Features()
        loadedFeatures.reset window.KomooNS.features

        featuresView = new FeaturesView
            collection: loadedFeatures


        $('.features-wrapper').append featuresView.render().$el

