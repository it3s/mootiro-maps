define ['lib/underscore-min', 'lib/backbone-min'], () ->
    $ = jQuery

    window.Feature = Backbone.Model.extend
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
        initialize: () ->
        model: Feature


    window.FeaturesView = Backbone.View.extend
        initialize: (attr) ->
            _.bindAll this, 'render'

            @type = attr.type
            @template = _.template $('#features-template').html()
            @collection.bind 'reset', @render

        title: ->
            if @type is 'OrganizationBranch'
                "#{@collection.length} points on map"
            else if @type is 'Community'
                "On #{@collection.length} communities"
            else if @type is 'SupportedOrganizationBranch'
                "Supported #{@collection.length} organizations"
            else if @type is 'Resource'
                "Supported #{@collection.length} resources"
            else if @type is 'Need'
                "Supported #{@collection.length} needs"
            else
                ""

        iconClass: ->
            if @type in ['OrganizationBranch', 'SupportedOrganizationBranch']
                modelName = 'Organization'
            else
                modelName = @type
            "icon-#{modelName.toLowerCase()}-big"


        render: () ->
            @$el.html @template(
                title: @title()
                iconClass: @iconClass()
            )
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
        KomooNS.features = _(geojson.features).groupBy (f) -> f.properties.type

        communitiesView = new FeaturesView
            type: 'Community'
            collection: new Features().reset KomooNS.features['Community']
        $('.features-wrapper').append communitiesView.render().$el

        needsView = new FeaturesView
            type: 'Need'
            collection: new Features().reset KomooNS.features['Need']
        $('.features-wrapper').append needsView.render().$el

        resourcesView = new FeaturesView
            type: 'Resource'
            collection: new Features().reset KomooNS.features['Resource']
        $('.features-wrapper').append resourcesView.render().$el

        branchsView = new FeaturesView
            type: 'OrganizationBranch'
            collection: new Features().reset _.filter(KomooNS.features['OrganizationBranch'], (o) =>
                o.properties.organization_name is KomooNS.obj.name)
        $('.features-wrapper').append branchsView.render().$el

        supportedBranchsView = new FeaturesView
            type: 'SupportedOrganizationBranch'
            collection: new Features().reset _.filter(KomooNS.features['OrganizationBranch'], (o) =>
                o.properties.organization_name isnt KomooNS.obj.name)
        $('.features-wrapper').append supportedBranchsView.render().$el

        geoObjectsListing $('.features-wrapper')

