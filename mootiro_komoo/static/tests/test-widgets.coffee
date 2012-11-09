require [
    'jquery',
    'sinon',
    'widgets/autocomplete'
], ($, sinon, AutocompleteView) ->

    ac = null
    $input = null
    module 'Autocomplete',
        setup: =>
            ac = new AutocompleteView 'ac_name', '/url/to/request/'
            ac.render()
            $input = ac.$input
        teardown: =>
            ac = null
            $input = null

    test 'constructor', ->
        ac = new AutocompleteView 'ac_name', '/url/to/request/'
        ok ac.$el
        ok $input
        equal $input.prop('tagName'), 'INPUT'
        equal $input.attr('type'), 'text'
        equal $input.attr('id'), 'id_ac_name_autocomplete'
        ok $input.hasClass 'ui-autocomplete-input'

    test 'ajax request on keydown', ->
        sinon.stub $, 'ajax'
        $input.val 'test'
        event = $.Event 'keydown'
        event.keyCode = 40
        $input.trigger event
        equal $.ajax.getCall(0).args[0].url, '/url/to/request/'
        deepEqual $.ajax.getCall(0).args[0].data, {term: 'test'}
        $.ajax.restore()
