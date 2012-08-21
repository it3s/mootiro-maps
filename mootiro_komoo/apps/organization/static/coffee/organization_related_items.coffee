define ['lib/underscore-min', 'lib/backbone-min'], () ->
    $ = jQuery

    window.PanelInfo = Backbone.Model.extend

        toJSON: (attr) ->
            Backbone.Model.prototype.toJSON.call this, attr


    window.PanelInfoView = Backbone.View.extend
        className: 'panel-info'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template $('#panel-info-template').html()

        render: () ->
            console.log 'rendering model: ', @model.toJSON()
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

    window.OrganizationFeaturesView = FeaturesView.extend
        title: (count) ->
            msg =
                if @type is 'OrganizationBranch'
                    ngettext("%s point on map",
                        "%s points on map",
                        count)
                else if @type is 'SupportedOrganizationBranch'
                    ngettext("Supported %s organization",
                        "Supported %s organizations",
                        count)
                else if @type is 'Community'
                    ngettext("On %s community",
                        "On %s communities",
                        count)
                else if @type is 'Resource'
                    ngettext("Supported %s resource",
                        "Supported %s resources",
                        count)
                else if @type is 'Need'
                    ngettext("Supported %s need",
                        "Supported %s needs",
                        count)
                else
                    ""
            interpolate msg, [count]

    $ ->
        KomooNS.drawFeaturesList OrganizationFeaturesView

        panelInfoView = new PanelInfoView
            model: new PanelInfo KomooNS.obj

        $('.panel-info-wrapper').append panelInfoView.render().$el
