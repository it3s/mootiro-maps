// alert('search js');
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
            data: {query: search_field.val(), 'csrfmiddlewaretoken': csrftoken},
            dataType: 'json',
            success: function(data){
                console.dir(data);
                search_results.find('div').remove();

                lis = '';
                data.result.forEach(function(obj){
                    lis += '<li> &raquo;&nbsp;' + obj.name +  '</li>';
                });

                search_results.append('' +
                    '<div>' +
                        '<h3>' + gettext('Search Results:') + '</h3>' +
                        '<ul>' +
                            lis +
                        '</ul>' +
                    '</div>'
                );

            }
        });
    });

})(jQuery);
