(function($){
    var form_search = $('#search'),
        search_field = $('#search-bar'),
        search_results = $('#search-results');
        csrftoken= getCookie('csrftoken');

    form_search.submit(function(evt){
        evt.preventDefault();
        console.log('searching for: ' + search_field.val());

        $.ajax({
            type: 'POST',
            url: dutils.urls.resolve('komoo_search'),
            data: {term: search_field.val(), 'csrfmiddlewaretoken': csrftoken},
            dataType: 'json',
            success: function(data){
                console.dir(data);
                search_results.find('div').remove();

                results_list = '';
                $.each(data.result, function(key, val){
                    if (val.length){
                        results_list += '<li><div class="search-header">' +
                            '<img src="/static/img/' + key + '.png" >' +
                            '<div class="search-type-header" >' +
                                key +
                                '<span class="search-results-count"> ' +
                                    val.length + ' ' + gettext("results") +
                                '</span>' +
                            '</div>' +
                       ' </div><ul class="search-result-entries">';
                        val.forEach(function(obj){
                            results_list += '<li><a href="' +  obj.link + '" >' + obj.name +  '</a></li>';
                        });
                        results_list += '</ul></li>';
                    } else {
                        results_list = '<div class="search-no-results">' + gettext('No results found!') + '</div>';
                    }
                });

                search_results.append('' +
                    '<div>' +
                        '<span class="search-title button">' + gettext('Search Results:') + '</span>' +
                        '<ul>' +
                        results_list +
                        '</ul>' +
                    '</div>'
                );

            }
        });
    });

})(jQuery);
// <span class="search-title button">Search Results: </span>
// <ul>
    // <li>
        // <div class="search-header">
            // <img src='/static/img/need.png'>
            // <div class='inline-block'>Need</div>
        // </div>
        // <ul class="search-result-entries">
            // <li>Uma entrada</li>
            // <li>Outra</li>
        // </ul>
    // </li>
// </ul>
