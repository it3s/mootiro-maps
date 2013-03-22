define (require) ->
    'use strict'

    $ = require 'jquery'

    class Component
        name: 'Base Component'
        description: ''
        enabled: off

        constructor: (@mediator, @el) ->
            @map = @mediator
            @$el = $(document).find(@el)

        setMap: (@map) ->

        enable: -> @enabled = on

        disable: -> @enabled = off

        init: (opts) ->
            return $.when(opts)

        destroy: () ->
            return true


    exports = Component

    return exports
