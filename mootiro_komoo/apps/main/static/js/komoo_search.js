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
    };

    var showResults = function (results){
        console.dir(results);
        $('#search-results-box').popover({
            placement: 'bottom',
            selector: search_field,
            trigger: 'manual',
            title: 'teste<span id="search-box-close" >x</span>',
            content: 'working?'
        })
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

    $('#search-box-close').live('click', function(){
        $('#search-results-box').popover('hide');
    });

});
