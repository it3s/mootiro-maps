define ['backbone', 'underscore', 'text!templates/map/_searchbox.html'], (Backbone, _, tplt) ->
    SearchBoxView = Backbone.View.extend
        events:
            'click .search': 'onSearchBtnClick'
            'change .location-type': 'onTypeChange'

        initialize: () ->
            @template = _.template tplt

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

    SearchBoxView: SearchBoxView
