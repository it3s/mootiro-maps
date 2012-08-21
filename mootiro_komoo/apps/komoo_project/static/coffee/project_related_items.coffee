define ['lib/underscore-min', 'lib/backbone-min'], () ->
    $ = jQuery

    window.PartnersLogo = Backbone.Model.extend
        toJSON: (attr) ->
            Backbone.Model.prototype.toJSON.call this, attr

    window.PartnersLogoView = Backbone.View.extend
        className: 'partner-logo'
        tagName: 'li'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template '<img src="<%= url %>" />'

        render: () ->
            console.log 'rendering model: ', @model.toJSON()
            renderedContent = @template @model.toJSON()
            $(@el).html renderedContent
            this

    window.PartnersLogos = Backbone.Collection.extend
        model: PartnersLogo

    window.PartnersLogosView = Backbone.View.extend
        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template '<ul class="partners-logo-list"></ul>'
            @collection.bind 'reset', @render

        render: () ->
            collection = @collection
            @$el.html @template()
            $logos = this.$ '.partners-logo-list'

            collection.each (logo) ->
                console.log '-----', logo
                view = new PartnersLogoView
                    model: logo
                $logos.append view.render().$el
            this

    $ ->
        KomooNS.drawFeaturesList()

        panelInfoView = new PanelInfoView
            model: new PanelInfo KomooNS.obj
        $('.panel-info-wrapper').append panelInfoView.render().$el

        partnersLogosView = new PartnersLogosView
            collection: new PartnersLogos().reset KomooNS.obj.partners_logo
        $('.panel-info-wrapper').append partnersLogosView.render().$el

