class ScriptLoader
    constructor: ->
        @waitting = {}
        @loading = []
        @loaded = []

    load: (name, url, callback) ->
        if name in @loaded
            console?.log "#{name} (#{url}) already loaded."
            callback? name
        else if name in @loading
            console?.log "#{name} (#{url}) is been loaded."
            @waitFor name, callback
        else
            @loading.push name
            $.ajax(url: url, dataType: "script", cache: true).done((script, status) =>
                @loaded.push name
                console?.log "#{name} (#{url}) loaded."
                callback? name
                while cb = @waitting[name]?.pop()
                    console?.log "calling callback for #{name}"
                    cb name
            ).fail((jqxhr, settings, exception) => console.log exception )

    waitFor: (name, callback) ->
        @waitting[name] ?= []
        @waitting[name].push callback
        if name in @loaded
            callback? name

window.scriptLoader ?= new ScriptLoader()
