$(function() {

    var form_search = $('#search'),
        search_field = $('#search-bar'),
        csrftoken = getCookie('csrftoken') || window.csrf_token;


    var titles = {
        'community': gettext('Communities'),
        'need': gettext('Needs'),
        'organization': gettext('Organizations'),
        'resource': gettext('Resources'),
        'investiment': gettext('Investments'),
        'google': gettext('Google Results')
    };

    // TODO: this should go to global.html
    form_search.after('<div id="search-results-box"></div>');

    var showPopover = function(){
        $('#search-results-box').popover('show');
        $('.popover').css('top', parseInt($('.popover').css('top')) - 10);
        $('.popover').css('left', parseInt($('.popover').css('left')) - 75);
    };

    var showResults = function (result){

        var results_list = '';
        var results_count = 0;
        var has_results = false;
        var result_order = ['community', 'organization', 'need', 'resource'];
        $.each(result_order, function(idx, key){
            var val = result[key];
            if (val.length && key !== 'google'){
                results_list += '<li><div class="search-header">' +
                    '<img src="/static/img/' + key + '.png" >' +
                    '<div class="search-type-header" >' +
                        titles[key] +
                        '<span class="search-results-count"> ' +
                            interpolate(
                                ngettext("%s result", "%s results", val.length),
                                [val.length]
                            ) +
                        '</span>' +
                    '</div>' +
               ' </div><ul class="search-result-entries">';
                val.forEach(function(obj){
                    results_list += '<li><a href="' +  obj.link + '" >' + obj.name +  '</a></li>';
                    results_count++;
                });
                results_list += '</ul></li>';
                has_results |= true;
            } else {
                // results_list = '<div class="search-no-results">' + gettext('No results found!') + '</div>';
                has_results |= false;
            }
        });

        // Google Results
        var google_results = JSON.parse(result.google).predictions;
        if (google_results && google_results.length){
            var key = 'google';
            results_list += '<li><div class="search-header">' +
                '<img src="/static/img/' + key + '.png" >' +
                '<div class="search-type-header" >' +
                    titles[key] +
                    '<span class="search-results-count"> ' +
                        interpolate(
                            ngettext("%s result", "%s results", google_results.length),
                            [google_results.length]
                        ) +
                    '</span>' +
                '</div>' +
           ' </div><ul class="search-result-entries">';
            google_results.forEach(function(obj){
                results_list += '<li><a href="#" onclick="editor.goTo(\'' + obj.description + '\'); return false;" >' + obj.description +  '</a></li>';
                results_count++;
            });
            results_list += '</ul></li>';
            has_results |= true;
        } else {
            has_results |= false;
        }


        if (! has_results) {
            results_list = '<div class="search-no-results">' + gettext('No results found!') + '</div>';
        }

        // Display results
        $('#search-results-box').data('popover').options.title = '' +
            results_count + ' Results <span id="search-box-close" >x</span>';

        $('#search-results-box').data('popover').options.content = results_list;

        showPopover();
    };

    form_search.submit(function(evt){
        evt.preventDefault();

        // Komoo Search
        $.ajax({
            type: 'POST',
            url: dutils.urls.resolve('komoo_search'),
            data: {term: search_field.val(), 'csrfmiddlewaretoken': csrftoken},
            dataType: 'json',
            success: function(data){
                showResults(data.result);
            }
        });

    });

    $('#search-results-box').popover({
        placement: 'bottom',
        selector: search_field,
        trigger: 'manual',

    });

    $('#search-box-close').live('click', function(){
        $('#search-results-box').popover('hide');
    });

});
