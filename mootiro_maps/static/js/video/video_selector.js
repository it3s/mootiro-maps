$(function() {

window.get_videos_list = function(){
    var list = [];
    $('#videolist .video-entry').each(function(idx, obj){
        if (!$(this).is('.video-error') && $(this).attr('data-status')){
            var id = '';
            if ($(this).attr('data-new') == 'false') {
                id = $(this).attr('data-id');
            }
            list.push({
                id: id,
                status: $(this).attr('data-status'),
                service: $(this).attr('data-service'),
                video_id: $(this).attr('data-video-id'),
                video_url: $(this).attr('data-video-url'),
                thumbnail_url: $(this).attr('data-thumbnail-url'),
                title: $(this).attr('data-title'),
                description: $(this).attr('data-description')
            });
        }

    });
    return list;
};

var new_id_count = 0;

window.add_video = function(video){
    var _new = false;
    if (video.id === undefined) {
        video.id = 'new_' + new_id_count++ ;
        video.status = 'modified';
        _new = true;
    }
    $('#videolist').append(
        '<div id="' + video.video_id +
        '" class="video-entry" data-video-id="'+ video.video_id +
        '" data-id="' + video.id +
        '" data-status="' + video.status +
        '" data-new="' + _new +
        '" data-service="' + video.service +
        '" data-title="' + video.title +
        '" data-description="' + video.description +
        '" data-video-url="' + video.video_url +
        '" data-thumbnail-url="' + video.thumbnail_url + '">' +
            '<strong class="video-title">' + video.title + '</strong>' +
            '<img src="' + video.thumbnail_url + '" alt="img" class="video-thumb">' +
        '</div>'
    );
};

$('.add-new-video-link').click(function(){
    var input = $("<input type='text' class='video-link' name='video_link'>");
    $('.video-link-list').append(input);
    input.focus();

});

$('#add_videos_from_links').click(function(evt){
    var requests = [];
    var errors = [];
    $('.video-modal input[name=video_link]').each(function(idx, el){
        var url = $(el).val();
        if (url.search('iframe') != -1) {
            var iframe = $(url);
            url = iframe.attr('src');
        }
        if (url) { // Ignore empty fields
            var post = $.post(
                dutils.urls.resolve('video_url_info'),
                {
                    video_url: url,
                    csrfmiddlewaretoken : getCookie('csrftoken')
                },
                function(data){
                    if (data.success) {
                        add_video(data.video)
                    } else {
                        errors.push(url);
                    }
                },
                'json'
            );
            requests.push(post);
        }
    });

    $.when.apply($, requests).then(function() {
        if (errors.length) {
            var urls = errors.join(', ');
            errorMessage(
                gettext('Invalid URL'),
                interpolate(gettext('The following urls could not be resolved as valid videos: %s'), [urls])
            );
        }
    });

    $('.video-modal').modal('hide');
    $('.video-modal input').remove();
    $('.video-link-list').append(''+
        "<input type='text' class='video-link' name='video_link'>"
    );

    return false;
});

$('.close').live('click', function(){
    $(this).parent().slideUp();
});

$('.video-entry').live('click', function(ev){
    if (isAuthenticated){
        var id  = $(this).attr('data-id');
        var video_title  = $(this).attr('data-title');
        var video_description  = $(this).attr('data-description');
        var video_thumb  = $(this).attr('data-thumbnail-url');

        $('#title-modal #video-title-modal').attr('src', video_thumb);
        $('#title-modal #id_title').val(video_title || '');
        $('#title-modal #id_description').val(video_description || '');
        $('#title-modal #id_title').attr('data-id', id);
        $('#title-modal #id_description').attr('data-id', id);
        $('#title-modal #delete-video').attr('data-id', id);
        $('#title-modal').modal('show');

        return false;
    } else {

        ev.stopPropagation();
        ev.stopImmediatePropagation();
        ev.preventDefault();
        url = document.location.pathname;

        $("#login-box #login-button").attr("href", "/user/login?next=" + url);
        $("#login-box").dialog({
            width: 850,
            modal: true,
            resizable: false,
            draggable: false
        });
        return false;
    }
});

$('#save-title').live('click', function(){
    var id = $('#title-modal #id_title').attr('data-id');
    var title = $('#title-modal #id_title').val();
    var description = $('#title-modal #id_description').val();

    var entry = $('#videolist .video-entry[data-id='+id+']');
    entry.attr('data-title', title).attr('data-description', description);
    entry.attr('data-status', 'modified');
    entry.find('.video-title').text(title);

    $('#title-modal').modal('hide');

    return false;
});

$('#delete-video').live('click', function(){
    if (confirm(gettext('Are you sure that you want to remove this video?'))){

        var id = $(this).attr('data-id');
        var entry = $('#videolist .video-entry[data-id='+id+']');
        var is_new = entry.attr('data-new');

        if (is_new == 'true') {
            entry.remove();
        } else {
            entry.attr('data-status', 'deleted');
            entry.hide();
        }
        $('#title-modal').modal('hide');

    }

    return false;
});

// Client side form validation
$('form').submit(function(e) {
    $('#id_videos_list').val(JSON.stringify(get_videos_list()));

});

});  //end document ready
