define ['jquery', 'underscore', 'backbone', 'related_items_panel'], ($, _, Backbone, drawFeaturesList) ->

    window.OrganizationFeaturesView = FeaturesView.extend
        title: (count) ->
            msg =
                if @type is 'SelfOrganizationBranch'
                    ngettext("%s point on map",
                        "%s points on map",
                        count)
                else if @type is 'OrganizationBranch'
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
        drawFeaturesList OrganizationFeaturesView

        panelInfoView = new PanelInfoView
            model: new PanelInfo KomooNS.obj

        $('.panel-info-wrapper').append panelInfoView.render().$el
