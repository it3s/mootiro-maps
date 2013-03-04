$ ->

    form_search = $ '#search form'
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
        # 'google': gettext 'Google Results'
        'user': gettext 'User'
        'project': gettext 'Project'

    showPopover = ->
        window.is_search_results_open = yes
        $('#search-results-box').popover 'show'

    hidePopover = ->
        window.is_search_results_open = no
        $('#search-results-box').popover 'hide'



    window.seeOnMap = (hashlink) ->

        if window.location.pathname == dutils.urls.resolve 'map'
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

            hidePopover()
        else
            window.location = dutils.urls.resolve('map') + "##{hashlink}"


    showResults = (result, search_term="") ->
        results_list = ''
        results_count = 0
        has_results = false

        if result?.length
            results_list += """
                <li>
                <ul class='search-result-entries'>
            """

            for idx, obj of result
                # disabled = if not obj?.has_geojson then 'disabled' else ''
                results_list += """
                    <li class="search-result">
                        <img class="model-icon" alt="icon #{obj.model}" title="icon #{obj.model}" src="/static/img/#{obj.model}.png">
                        <a class="search-result-title" href='#{obj.link}'> #{obj.name} </a>
                        <div class="right">
                            <a href="/map/##{obj.hashlink}" hashlink="#{obj.hashlink}" class="search-map-link #{obj.disabled}" title="ver no mapa"><i class="icon-see-on-map"></i></a>
                        </div>
                    </li>"""

                results_count++
            results_list += "<li class='search-results-see-all'><a href='/search/all?term=#{search_term}'> ver todos &raquo;</a> </li></ul></li>"
            has_results |= yes

        else
            has_results |= no



        if not has_results
            results_list = """<div class="search-no-results"> #{ gettext('No results found!') }</div>"""

        $('#search-results-box').data('popover').options.content = results_list
        showPopover()
        cl.hide()

    doSearch = ->
        window.komoo_search_timeout_fn = null
        search_term = search_field.val()

        if not search_term
            return

        cl.show()

        # Komoo Search
        $.ajax
            type: 'POST'
            url: dutils.urls.resolve('komoo_search')
            data: {term: search_term, 'csrfmiddlewaretoken': csrftoken}
            dataType: 'json'
            success: (data) ->
                # localStorageSet 'komoo_search', {
                #     term: search_term
                #     results: data.result
                # }
                showResults data.result, search_term


    form_search.submit (evt) ->
        evt.preventDefault()
        if window.komoo_search_timeout_fn
            clearTimeout window.komoo_search_timeout_fn
        doSearch()

    window.komoo_search_timeout_fn = null
    search_field.bind 'keydown', ->
        if search_field.val().length > 2
            if window.komoo_search_timeout_fn
                clearTimeout window.komoo_search_timeout_fn
            window.komoo_search_timeout_fn = setTimeout doSearch, 500


    $('#search-results-box').popover
        placement: 'bottom'
        selector: search_field
        trigger: 'manual'
        animation: true

    $('body').live 'click', (evt) ->
      result_box = $('.popover')
      if window.is_search_results_open and result_box.has(evt.target).length == 0
        hidePopover()

    $('.search-map-link').live 'click', (evt) ->
        evt.preventDefault()
        _this = $ this
        if not _this.is '.disabled'
            seeOnMap _this.attr 'hashlink'
        else
            return false

    # See on Map
    if window.location.pathname == dutils.urls.resolve('map')
        hash = window.location.hash
        seeOnMap(hash.substring(1, hash.length)) if hash

