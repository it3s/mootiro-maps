define (require) ->

    _ = require 'underscore'
    Backbone = require 'backbone'

    class SearchBoxView extends Backbone.View
        events:
            'click .search': 'onSearchBtnClick'
            'change .location-type': 'onTypeChange'

        initialize: () ->
            @template = _.template require 'text!templates/map/_searchbox.html'

        render: () ->
            renderedContent = @template()
            @$el.html renderedContent
            this

        onTypeChange: () ->
            type = @$('.location-type').val()
            if type == 'address'
                @$('.latLng-container').hide()
                @$('.address-container').show()
            else
                @$('.address-container').hide()
                @$('.latLng-container').show()

        onSearchBtnClick: () ->
            type = @$('.location-type').val()
            position = if type == 'address'
                @$('.address').val()
            else
                [
                    parseFloat(@$('.lat').val().replace(',', '.')),
                    parseFloat(@$('.lng').val().replace(',', '.'))
                ]

            @search type, position
            false

        search: (type='address', position) ->
            @trigger 'search',
                type: type
                position: position
            this


    class LayersBoxView extends Backbone.View
        events:
            'click .layer': 'toggleLayer'

        initialize: () ->
            @template = _.template require 'text!templates/map/_layersbox.html'

        render: (@layers) ->
            renderedContent = @template(layers: @layers)
            @$el.html renderedContent
            this

        toggleLayer: (evt) ->
            $el = @$ evt.target
            layer = $el.attr 'data-layer'
            visible = @layers.getLayer(layer).toggle()
            $el.attr 'data-visible', visible

    SearchBoxView: SearchBoxView
    LayersBoxView: LayersBoxView
