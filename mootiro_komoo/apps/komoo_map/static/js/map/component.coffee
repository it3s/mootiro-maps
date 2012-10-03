define ['jquery'], ($) ->
    'use strict'


    class Component
        name: 'Base Component'
        description: ''
        enabled: off

        constructor: (@mediator, @el) ->
            @map = @mediator
            @$el = $(document).find(@el)

        setMap: (@map) ->
            #console?.warn 'setMap method is deprecated. Please subscribe to "Map:started" message instead.'

        enable: -> @enabled = on

        disable: -> @enabled = off

        init: (opts) ->
            return $.when(opts)

        destroy: () ->
            return true


    exports = Component

    return exports
