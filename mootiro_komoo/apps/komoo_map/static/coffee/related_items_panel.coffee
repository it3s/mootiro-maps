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

        title: (count) ->
            msg =
                if @type is 'OrganizationBranch'
                    ngettext("%s organization branch",
                        "%s organization branchs",
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
                        "%{s needs",
                        count)
                else
                    ""
            interpolate msg, [count]

        iconClass: ->
            if @type in ['OrganizationBranch', 'SupportedOrganizationBranch']
                modelName = 'Organization'
            else
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

        branchsView = new FeaturesViewClass
            type: 'OrganizationBranch'
            collection: new Features().reset _.filter(KomooNS.features['OrganizationBranch'], (o) =>
                o.properties.organization_name is KomooNS.obj.name)
        $('.features-wrapper').append branchsView.render().$el

        supportedBranchsView = new FeaturesViewClass
            type: 'SupportedOrganizationBranch'
            collection: new Features().reset _.filter(KomooNS.features['OrganizationBranch'], (o) =>
                o.properties.organization_name isnt KomooNS.obj.name)
        $('.features-wrapper').append supportedBranchsView.render().$el

        geoObjectsListing $('.features-wrapper')

