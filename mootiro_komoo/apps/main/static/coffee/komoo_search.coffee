$ ->

    form_search = $ '#search'
    search_field = $ '#search-bar'
    csrftoken = getCookie('csrftoken') or  window.csrf_token

    # canvas loader for user feedback
    cl = new CanvasLoader 'search-canvasloader-container'
    cl.setColor '#3ebac2'
    cl.setShape 'rect'
    cl.setDiameter 22
    cl.setDensity 43
    cl.setRange 1.2
    cl.setFPS 22

    titles =
        'community': gettext 'Communities'
        'need': gettext 'Needs'
        'organization': gettext 'Organizations'
        'resource': gettext 'Resources'
        'investiment': gettext 'Investments'
        'google': gettext 'Google Results'

    showPopover = ->
        $('#search-results-box').popover 'show'
        $('.popover').css 'top', parseInt($('.popover').css('top'), 10) - 10
        $('.popover').css 'left', parseInt($('.popover').css('left'), 10) - 75


    window.seeOnMap = (hashlink) ->
        if window.location.pathname == dutils.urls.resolve 'map'
            if hashlink[0] is 'g'
                idx = parseInt hashlink.substring(1, hashlink.length), 10
                itvl = setInterval () ->
                        try
                            desc = JSON.parse(localStorageGet('komoo_search').results['google']).predictions[idx].description
                            editor.goTo desc
                            clearInterval itvl
                    ,500

            else
                # XhR
                $.get(
                    '/map/get_geojson_from_hashlink/'
                    {hashlink: hashlink}
                    (data) ->
                        geojson = JSON.parse(data.geojson)
                        itvl = setInterval () ->
                            try
                                editor.loadGeoJSON(geojson, true)
                                clearInterval itvl
                        ,500

                    'json'
                )

            $('#search-results-box').popover 'hide'
        else
            window.location = dutils.urls.resolve('map') + "##{hashlink}"


    showResults = (result) ->
        results_list = ''
        results_count = 0
        has_results = false
        result_order = ['community', 'organization', 'need', 'resource']

        for key in result_order
            val = result[key]

            if val?.length and key isnt 'google'
                results_list += """
                    <li>
                    <div class='search-header #{key}' >
                        <img src='/static/img/#{key}.png' >
                        <div class='search-type-header' >
                            #{titles[key]}
                            <span class='search-results-count'>
                                #{interpolate(
                                    ngettext('%s result', '%s results', val.length),
                                    [val.length]
                                )}
                            </span>
                        </div>
                    </div>
                    <ul class='search-result-entries'>
                """

                for idx, obj of val
                    geojson = JSON.parse(obj?.geojson ? {})
                    disabled = if not geojson?.features[0]?.geometry then 'disabled' else ''
                    hashlink = key[0] + obj.id
                    results_list += """
                        <li>
                            <a href='#{obj.link}'> #{obj.name} </a>
                            <div class="right">
                                <a href="/map/##{hashlink}" onclick="seeOnMap('#{hashlink}')" class="#{disabled}"><i class="icon-see-on-map"></i></a>
                            </div>
                        </li>"""
                    results_count++
                results_list += '</ul></li>'
                has_results |= yes

            else
                has_results |= no

        # Google Results
        google_results = JSON.parse(result.google).predictions
        if google_results?.length
            key = 'google'
            results_list += """
                <li>
                <div class="search-header google">
                    <img src="/static/img/#{key}.png" >
                    <div class="search-type-header" >
                        #{titles[key]}
                        <span class="search-results-count">
                            #{interpolate(
                                ngettext("%s result", "%s results", google_results.length),
                                [google_results.length]
                            )}
                        </span>
                    </div>
                </div>
                <ul class="search-result-entries">
            """
            for idx, obj of google_results
                hashlink = "g#{idx}"
                results_list += """
                    <li>
                        <a href="#" > #{obj.description}</a>
                        <div class="right">
                            <a href="##{hashlink}" onclick=seeOnMap('#{hashlink}')><i class="icon-see-on-map"></i></a>
                        </div>
                    </li>
                """
                results_count++
            results_list += '</ul></li>'
            has_results |= yes
        else
            has_results |= no


        if not has_results
            results_list = """<div class="search-no-results"> #{ gettext('No results found!') }</div>"""

        # Display results
        $('#search-results-box').data('popover').options.title = """
            #{results_count} Results <span id="search-box-close" >x</span>
        """
        $('#search-results-box').data('popover').options.content = results_list
        showPopover()
        cl.hide()


    form_search.submit (evt) ->
        evt.preventDefault()

        search_term = search_field.val()
        previous_search = localStorageGet 'komoo_search'

        if not search_term
            return

        cl.show()

        if previous_search?.term is search_term
            showResults previous_search.results
        else
            # Komoo Search
            $.ajax
                type: 'POST'
                url: dutils.urls.resolve('komoo_search')
                data: {term: search_term, 'csrfmiddlewaretoken': csrftoken}
                dataType: 'json'
                success: (data) ->
                    localStorageSet 'komoo_search', {
                        term: search_term
                        results: data.result
                    }
                    showResults data.result

    $('#search-results-box').popover
        placement: 'bottom'
        selector: search_field
        trigger: 'manual'

    $('#search-box-close').live 'click', ->
        $('#search-results-box').popover 'hide'

    # load last search term
    search_field.val(localStorageGet('komoo_search')?.term or '')

    # See on Map
    if window.location.pathname == dutils.urls.resolve('map')
        hash = window.location.hash
        seeOnMap(hash.substring(1, hash.length)) if hash

