define [
    'jquery',
    'underscore',
    'backbone',
    'text!templates/widgets/_autocomplete.html',
    'jquery-ui'
], ($, _, Backbone, tplt) ->
    AutocompleteView = Backbone.View.extend
        className: 'autocomplete'
        inputName: 'autocomplete'
        autocompleteSource: '/autocomplete/'

        initialize: (inputName, autocompleteSource) ->
            @inputName = inputName or @inputName
            @autocompleteSource = autocompleteSource or @autocompleteSource

            @template = _.template tplt

        clear: () ->
            @$input.val ''
            @$value.val ''

        val: () ->
            console.log 'value', @$value.val()
            @$value.val()

        render: () ->
            renderedContent = @template
                name: @inputName
            @$el.html renderedContent

            @$input = @$el.find "#id_#{@inputName}_autocomplete"
            @$value = @$el.find "#id_#{@inputName}"

            @$input.autocomplete
                source: @autocompleteSource,
                focus: (event, ui) =>
                    @$input.val ui.item.label
                    return false
                select: (event, ui) =>
                    @$input.val ui.item.label
                    @$value.val ui.item.value
                    return false
                change: (event, ui) =>
                    if(!ui.item || !@$input.val())
                        @clear()
            this

    AutocompleteView
