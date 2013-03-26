define (require) ->
    'use strict'

    $ = require 'jquery'
    _ = require 'underscore'
    Backbone = require 'backbone'

    # We use the mediator pattern
    class Mediator
        loading: 0

        data:
            deferred: $.Deferred
            when: $.when

        constructor: ->
            @_components = {}
            @_hooks = {}
            @_pubQueue = []
            @_pubsub = {}
            _.extend(@_pubsub, Backbone.Events)

        _getComponent: (component, id) ->
            components = @_components[component] ? {}
            if not components[id]?
                throw new Error "Could not be found a component '#{component}' with id '#{id}'"
            return components[id]

        _removeComponent: (component, id) ->
            delete @_components[component]?[id]

        registerHook: (hook, method, that=null) ->
            @_hooks[hook] ?= []
            console.log '--->', not (method in @_hooks[hook])
            @_hooks[hook].push _.bind(method, that) if not (method in @_hooks[hook])

        unregisterHook: (hook, method) ->
            # TODO

        triggerHooks: (hook, params...) ->
            for method in @_hooks[hook] ? []
                params = method(params...)
            params

        # Load the component module using AMD and instantiate the component
        load: (component, el, opts) ->
            id = el
            componentParts = component.split '::'
            componentModule = componentParts[0]
            componentName = componentParts[1]

            dfd = @data.deferred()
            require [componentModule], ((module) =>
                componentClass = module[componentName]

                # Lets create the component instance
                try
                    instance = new componentClass this, el
                catch e
                    console?.error e.message
                    console?.warn "Could not initialize component '#{component}'"
                    dfd.resolve()
                    return

                # Its time to initialize the component
                @data.when(instance.init(opts)).done(=>
                    # This component instance was initialized successfully
                    @_components[component][id].instance = instance
                    # Register the component hooks
                    for hook, method of instance.hooks
                        @registerHook hook, instance[method], instance if instance[method]?
                    # lets send the news to everybody
                    console?.log "Component '#{component}' initialized"
                    @publish "#{componentName}:started", id
                    dfd.resolve instance
                ).fail(=>
                    console?.warn "Could not initialize component '#{component}'"
                    dfd.resolve instance
                )
            ), ((e) =>
                if e.requireType is 'timeout'
                    console?.warn "Could not load module '#{e.requireModules}'"
                else
                    failedId = e.requireModules && e.requireModules[0]
                    require.undef failedId
                    console?.error e.message
                    console?.warn "Could not initialize component '#{component}'"
                dfd.resolve()
            )
            return dfd.promise()

        unload: (component) ->
            # TODO

        # component format is 'path/to/module::ComponentName'
        start: (componentList, el, opts={}) ->
            if _.isString componentList
                componentList_ = [
                    component: componentList
                    el: el
                    opts: opts
                ]
            else if not _.isArray componentList
                componentList_ = [componentList]
            else
                componentList_ = componentList

            if not _.isArray componentList_
                throw new Error 'componentList must be defined as an array'

            promises = []

            for item in componentList_
                component = item.component
                el = item.el
                opts = item.opts

                #console?.log "Starting component '#{component}'"
                @loading++

                # Two or more components can't be responsable for the same DOM
                # element, so we can use the element selector as id
                id = el

                @_components[component] ?= {}

                components = @_components[component]
                # We can't have more than one instance of the same component
                # using the same id
                if components[id]?
                    console?.error "Conflict: already exists one component '#{component}' with id '#{id}' "

                @_components[component][id] =
                    type: component
                    el: el
                    opts: opts

                dfd = @data.deferred()
                promises.push @load(component, el, opts)

            ret = @data.when.apply($, promises)
            ret.done =>
                @loading -= arguments.length
                @_processPublishQueue()
            return ret

        stop: (component, el) ->
            # Two or more components can't be responsable for the same DOM
            # element, so we can use the element selector as id
            id = el

            # We can receive only one element/id or a list
            ids = if not _.isArray id then [id] else id

            dfd = @data.deferred()
            len = ids.length
            done = 0

            for cid in ids
                component_ = @_getComponent component, cid
                # Tell the component instance to clear the house
                component_.instance.destroy().done(->
                    # The house is clear, its time to clear the DOM element
                    $(component_.el).children().remove()
                    # and remove the component instance reference
                    @_removeComponent component, cid

                    done++
                    # Just resolve the deferred return when all instances were
                    # cleaned
                    if done is len
                        dfd.resolve()
                )

            return dfd.promise()

        # We also use pub/sub pattern
        publish: (message) ->
            # Wait until all components were loaded to publish any message
            @_addToPublishQueue.apply this, arguments
            @_processPublishQueue()

        subscribe: (message, callback, context) ->
            @_pubsub.on message, callback, context

        _addToPublishQueue: (message) ->
            #console?.log "Adding message '#{message}' to publish queue"
            @_pubQueue.push arguments

        _processPublishQueue: () ->
            if @loading > 0
                return false
            message = @_pubQueue.shift()
            if message?
                #console?.log "Publishing message '#{message[0]}'"
                @_pubsub.trigger.apply @_pubsub, message
                @_processPublishQueue()


    exports =
        Mediator: Mediator

    return exports
