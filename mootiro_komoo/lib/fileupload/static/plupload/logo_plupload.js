$(function() {
    var logo_uploader = new plupload.Uploader({
        runtimes : 'html5,flash,gears,silverlight,browserplus',
        url : '/upload/new/',
        max_file_size : '10mb',
        chunk_size : '10mb',
        unique_names : true,
        browse_button : 'picklogo',
        container : 'logo-uploader',
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
        //add_file(resp);
        $('#id_logo').val(resp.id);
        $('#logo-thumb').html('' +
            '<img src="' + resp.url + '" >'
        );
    });
    logo_uploader.bind('Error', function(up, err) {
        alert(err);
        up.refresh(); // Reposition Flash/Silverlight
    });

});

