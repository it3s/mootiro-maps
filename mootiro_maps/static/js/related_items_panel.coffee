define ['jquery', 'underscore', 'backbone'], ($, _, Backbone) ->

    window.PanelInfo = Backbone.Model.extend
        toJSON: (attr) ->
            Backbone.Model.prototype.toJSON.call this, attr


    window.PanelInfoView = Backbone.View.extend
        className: 'panel-info'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template $('#panel-info-template').html()

        render: () ->
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

    window.Feature = Backbone.Model.extend
        toJSON: (attr) ->
            defaultJSON = Backbone.Model.prototype.toJSON.call this, attr
            name = @get('properties')?['organization_name'] ? ''
            if name
                name += ' - '
            name += @get('properties')?['name']
            _.extend defaultJSON,
                iconClass: @iconClass
                name: name

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
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

        displayOnMap: () ->
            @model.displayOnMap()
            this


    window.Features = Backbone.Collection.extend
        initialize: () ->
        model: Feature


    window.FeaturesView = Backbone.View.extend
        initialize: (attr) ->
            _.bindAll this, 'render'

            @type = attr.type
            @template = _.template $('#features-template').html()
            @collection.bind 'reset', @render

        title: (count) ->
            msg =
                if @type is 'Organization'
                    ngettext("%s organization",
                        "%s organizations",
                        count)
                else if @type is 'Community'
                    ngettext("%s community",
                        "%s communities",
                        count)
                else if @type is 'Resource'
                    ngettext("%s resource",
                        "%s resources",
                        count)
                else if @type is 'Need'
                    ngettext("%s need",
                        "%s needs",
                        count)
                else if @type is 'User'
                    ngettext("%s collaborator",
                        "%s collaborators",
                        count)
                else
                    ""
            interpolate msg, [count]

        iconClass: ->
            modelName = @type
            "icon-#{modelName.toLowerCase()}-big"


        render: () ->
            collection = @collection

            if collection.length is 0
                return this

            @$el.html @template(
                title: @title(collection.length)
                iconClass: @iconClass()
            )
            $features = this.$ '.feature-list'

            collection.each (feature) ->
                view = new FeatureView
                    model: feature
                    # collection: collection
                $features.append view.render().$el
            this

    KomooNS ?= {}
    KomooNS.drawFeaturesList = (FeaturesViewClass = FeaturesView) ->
        KomooNS.features = _(geojson.features).groupBy (f) -> f.properties.type

        communitiesView = new FeaturesViewClass
            type: 'Community'
            collection: new Features().reset KomooNS.features['Community']
        $('.features-wrapper').append communitiesView.render().$el

        needsView = new FeaturesViewClass
            type: 'Need'
            collection: new Features().reset KomooNS.features['Need']
        $('.features-wrapper').append needsView.render().$el

        resourcesView = new FeaturesViewClass
            type: 'Resource'
            collection: new Features().reset KomooNS.features['Resource']
        $('.features-wrapper').append resourcesView.render().$el

        organizationsView = new FeaturesViewClass
            type: 'Organization'
            collection: new Features().reset _.filter(KomooNS.features['Organization'], (o) =>
                o.properties.name isnt KomooNS.obj.name)
        $('.features-wrapper').append organizationsView.render().$el

        usersView = new FeaturesViewClass
            type: 'User'
            collection: new Features().reset KomooNS.features['User']
        $('.features-wrapper').append usersView.render().$el

        geoObjectsListing $('.features-wrapper')

    return KomooNS.drawFeaturesList
