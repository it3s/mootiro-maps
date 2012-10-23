$(function(){
    var logo_uploader = new plupload.Uploader({
        runtimes : 'html5,flash,gears,silverlight,browserplus',
        url : '/upload/new/',
        max_file_size : '10mb',
        chunk_size : '10mb',
        unique_names : true,
        browse_button : 'pick-file',
        container : 'file-uploader',
        multiple: false,

        filters : [
            {title : "Image files", extensions : "jpg,gif,png"},
            {title : "Zip files", extensions : "zip"}
        ],

        flash_swf_url : '/static/plupload/js/plupload.flash.swf',
        silverlight_xap_url : '/static/plupload/js/plupload.silverlight.xap',

        multipart_params : {
            "csrfmiddlewaretoken" : getCookie('csrftoken')
        }
    });

    logo_uploader.init();

    logo_uploader.bind('FilesAdded', function(up, files) {
        up.start();
    });

    logo_uploader.bind('FileUploaded', function(up, file, response) {
        var resp = JSON.parse(response.response);
        addFile(resp);
    });
    logo_uploader.bind('Error', function(up, err) {
        alert(err);
        up.refresh(); // Reposition Flash/Silverlight
    });

    var addFile = function(file) {
        $('#file-thumb').html(
            '<div id="' + file.id + '" class="file-entry" file-id="'+ file.id +'">' +
                '<img src="' + file.url + '" alt="img" class="file-thumb">' +
            '</div>'
        );
        $('.logo-input-field').val(file.id);

    };

    // file thumb modal box behavior
    // $('.close').live('click', function(){
    //     $(this).parent().slideUp();
    // });

    $('.file-thumb').live('click', function(ev){
        if (KomooNS && KomooNS.isAuthenticated){
            var file_id  = $(this).parent().attr('file-id');

            $.get(
                '/upload/file_info/',
                {'id': file_id},
                function(data){
                    $('#subtitle-modal #img-subtitle-modal').attr('src', data.url);
                    $('#subtitle-modal #id_subtitle').val(data.subtitle || '');
                    $('#subtitle-modal #id_subtitle').attr('file-id', file_id);
                    $('#subtitle-modal #delete-file').attr('file-id', file_id);
                    $('#subtitle-modal').modal('show');
                },
                'json'
            );

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
        }
        return false;
    });

    $('#save-subtitle').live('click', function(){
        var file_id = $('#subtitle-modal #id_subtitle').attr('file-id');
        var subtitle = $('#subtitle-modal #id_subtitle').val();
        $.post(
            '/upload/save_subtitle/',
            {
                id: file_id,
                subtitle: subtitle,
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
        if (confirm(gettext('Are you sure you want to delete this file?'))){

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

    // On load
    if ($('.logo-input-field').val()){
        var file_id = $('.logo-input-field').val();
        $.get(
            '/upload/file_info/',
            {'id': file_id},
            function(data){
                data.id = file_id;
                addFile(data);
            },
            'json'
        );

    }
});

