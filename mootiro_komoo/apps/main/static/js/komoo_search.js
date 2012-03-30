// alert('search js');
(function($){
    var form_search = $('#search'),
        search_field = $('#search-bar');
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
            }
        });
    });

})(jQuery);
