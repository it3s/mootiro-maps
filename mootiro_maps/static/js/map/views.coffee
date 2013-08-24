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
            'click .layer .item': 'toggleLayer'
            'click .layer .collapser': 'toggleSublist'
            'click .feature': 'highlightFeature'

        initialize: () ->
            @template = _.template require 'text!templates/map/_layersbox.html'

        render: (@layers) ->
            renderedContent = @template(layers: @layers)
            @$el.html renderedContent
            # Closes the sublists
            @$('.sublist').hide()
            this

        toggleLayer: (evt) ->
            $el = @$ evt.currentTarget
            layerId = $el.attr 'data-layer'
            isVisible = $el.attr('data-visible') is 'true'
            action =  if not isVisible then 'show' else 'hide'
            @trigger action, layerId
            $el.attr 'data-visible', not isVisible
            $el.toggleClass 'on off'

        toggleSublist: (evt) ->
            $collapser = @$ evt.currentTarget
            $sublist = $collapser.parent().next '.sublist'
            console.log $sublist
            $collapser.find('i').toggleClass 'icon-chevron-right icon-chevron-down'
            $sublist.toggle()

        highlightFeature: (evt) ->
            $el = @$ evt.currentTarget
            id = parseInt($el.attr 'data-id')
            @trigger 'highlight_feature', id


    SearchBoxView: SearchBoxView
    LayersBoxView: LayersBoxView
