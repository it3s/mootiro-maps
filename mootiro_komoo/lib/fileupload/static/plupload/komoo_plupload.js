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
            file.name + ' (' + plupload.formatSize(file.size) + ') <b></b>' +
        '</div>'
    );
};

// $('.file-delete').live('click', function(){
//     var delete_url = $(this).attr('delete-url');
//     $.post(
//         delete_url,
//         {csrfmiddlewaretoken: getCookie('csrftoken')},
//         function(data){
//             console.log(data);
//         },
//         'json');

//     $(this).parent().fadeOut();
// });


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
    console.log('here?');
});

uploader.bind('FileUploaded', function(up, file, response) {
    var resp = JSON.parse(response.response);
    console.dir(resp);
    add_file(resp);
});
uploader.bind('Error', function(up, err) {
    $('#filelist').append("" +
        "<div class=\"file-entry file-error\">" +
            (err.file ? "" +
                (
                    err.file.name + ' (' + plupload.formatSize(err.file.size) + ')'
                ) : "")  +
            "<br>" +
            "<strong>Erro</strong>: " + err.message +
        "</div>"
    );

    up.refresh(); // Reposition Flash/Silverlight
});


$('.add-new-file-link').click(function(){
    $('.file-link-list').append(''+
        "<input type='text' class='file-link' name='file_link'>");
});

$('#add_files_from_links').click(function(evt){
    // get links list
    $('.file-modal input[name=file_link]').each(function(idx, el){
        var link = $(el).val();
        $.post(
            '/upload/add_from_link/',
            {
                file_link: link,
                csrfmiddlewaretoken : getCookie('csrftoken')
            },
            function(data){
                console.dir(data);
                add_file(data.file)
                $('.file-modal').modal('hide');
            },
            'json'
        );
    });
});

// Client side form validation
$('form').submit(function(e) {
    $('#id_files_ids_list').val(get_files_list());

});
});
