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

    $ ->
        panelInfoView = new PanelInfoView
            model: new PanelInfo KomooNS.obj

        $('.panel-info-wrapper').append panelInfoView.render().$el
