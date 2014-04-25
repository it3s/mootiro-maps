$(function() {

window.get_files_list = function(){
    var ids_list = '';
    $('#filelist .file-entry:visible').each(function(idx, obj){
        if (!$(this).is('.file-error')){
            ids_list += $(this).attr('file-id') + '|';
        }

    });
    return ids_list;
};

window.add_file = function(file){
    $('#filelist').append(
        '<div id="' + file.id + '" class="file-entry" file-id="'+ file.id +'">' +
            // file.name + ' (' + plupload.formatSize(file.size) + ') <b></b>' +
            '<img src="' + file.url + '" alt="img" class="file-thumb">' +
        '</div>'
    );
};


var uploader = new plupload.Uploader({
    // General settings
    runtimes : 'html5,flash,gears,silverlight,browserplus',
    url : '/upload/new/',
    max_file_size : '10mb',
    chunk_size : '10mb',
    unique_names : true,
    browse_button : 'pickfiles',
    container : 'uploader',

    // Specify what files to browse for
    filters : [
        {title : "Image files", extensions : "jpg,gif,png"},
        {title : "Zip files", extensions : "zip"}
    ],

    // Flash settings
    flash_swf_url : '/static/plupload/js/plupload.flash.swf',

    // Silverlight settings
    silverlight_xap_url : '/static/plupload/js/plupload.silverlight.xap',

    multipart_params : {
        "csrfmiddlewaretoken" : getCookie('csrftoken')
    }
});

uploader.init();

uploader.bind('FilesAdded', function(up, files) {
    up.start();
});

uploader.bind('FileUploaded', function(up, file, response) {
    var resp = JSON.parse(response.response);
    add_file(resp);
});
uploader.bind('Error', function(up, err) {
    $('#filelist').prepend("" +
        "<div class=\"file-error\">" +
            "<span class='close'>x</span>" +
            (err.file ? "" +
                (
                    err.file.name + ' (' + plupload.formatSize(err.file.size) + ')'
                ) : "")  +
            "&nbsp;&nbsp;<strong>Erro</strong>: " + err.message +
        "</div>"
    );

    up.refresh(); // Reposition Flash/Silverlight
});


$('.add-new-file-link').click(function(){
    $('.file-link-list').append(''+
        "<input type='text' class='file-link' name='file_link'>");
});

$('#add_files_from_links').click(function(evt){
    $('.file-modal input[name=file_link]').each(function(idx, el){
        var link = $(el).val();
        $.post(
            '/upload/add_from_link/',
            {
                file_link: link,
                csrfmiddlewaretoken : getCookie('csrftoken')
            },
            function(data){
                add_file(data.file)
            },
            'json'
        );
    });

    $('.file-modal').modal('hide');
    $('.file-modal input').remove();
    $('.file-link-list').append(''+
        "<input type='text' class='file-link' name='file_link'>"
    );

});

$('.close').live('click', function(){
    $(this).parent().slideUp();
});

$('.file-thumb').live('click', function(ev){
    if (isAuthenticated){
        var file_id  = $(this).parent().attr('file-id');

        $.get(
            '/upload/file_info/',
            {'id': file_id},
            function(data){
                $('#subtitle-modal #img-subtitle-modal').attr('src', data.url);
                $('#subtitle-modal #id_subtitle').val(data.subtitle || '');
                $('#subtitle-modal #id_subtitle').attr('file-id', file_id);
                if (data.cover) {
                  $('#subtitle-modal #id_cover').attr('checked', 'checked');
                }
                $('#subtitle-modal #id_cover').attr('file-id', file_id);
                $('#subtitle-modal #delete-file').attr('file-id', file_id);
                $('#subtitle-modal').modal('show');
            },
            'json'
        );

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

$('#save-subtitle').live('click', function(){
    var file_id = $('#subtitle-modal #id_subtitle').attr('file-id');
    var subtitle = $('#subtitle-modal #id_subtitle').val();
    var cover = $('#subtitle-modal #id_cover').prop('checked');
    $.post(
        '/upload/save_subtitle/',
        {
            id: file_id,
            subtitle: subtitle,
            cover: cover,
            csrfmiddlewaretoken: getCookie('csrftoken')
        },
        function(data){
            $('#subtitle-modal').modal('hide');
        },
        'json'
    );

    return false;
});

$('#delete-file').live('click', function(){
    if (confirm(gettext('Are you sure that you want to delete this file?'))){

        var file_id = $(this).attr('file-id');
        $.post(
            '/upload/delete/' + file_id,
            {
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            function(data){
                $('#subtitle-modal').modal('hide');
                $('.file-entry[file-id=' + file_id + ']').fadeOut('slow', function(){
                    $(this).remove();
                });
            },
            'json'
        );

    }

    return false;
});

// Client side form validation
$('form').submit(function(e) {
    $('#id_files_ids_list').val(get_files_list());

});

});  //end document ready
