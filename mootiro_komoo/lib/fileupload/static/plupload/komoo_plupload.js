$(function() {

window.get_files_list = function(){
    var ids_list = '';
    $('#files-list .file-entry:visible').each(function(idx, obj){
        ids_list += $(this).attr('file-id') + '|';
    });
    return ids_list;
};

window.add_file = function(file){
    $('#files-list').append('' +
        '<div class="file-entry" file-id="' + file.id + '">' +
            '<img class="file-img" src="' + file.url + '">' +
             file.name +
             '<span class="file-delete" delete-url="'+ file.delete_url +'">x</span>' +
        '</div>'
    );
};

$('.file-delete').live('click', function(){
    var delete_url = $(this).attr('delete-url');
    $.post(
        delete_url,
        {csrfmiddlewaretoken: getCookie('csrftoken')},
        function(data){
            console.log(data);
        },
        'json');

    $(this).parent().fadeOut();
});


$("#uploader").pluploadQueue({
    // General settings
    runtimes : 'html5,flash,gears,silverlight,browserplus',
    url : '/upload/new/',
    max_file_size : '10mb',
    chunk_size : '10mb',
    unique_names : true,

    // Resize images on clientside if we can
    // resize : {width : 320, height : 240, quality : 90},

    // Specify what files to browse for
    filters : [
        {title : "Image files", extensions : "jpg,gif,png"},
        {title : "Zip files", extensions : "zip"}
    ],

    // Flash settings
    flash_swf_url : '/static/plupload/js/plupload.flash.swf',

    // Silverlight settings
    silverlight_xap_url : '/static/plupload/js/plupload.silverlight.xap',

    multiple_queues: true,
    // multi_selection:false,
    max_file_count: 5,

    drop_element: 'uploader',
    sortable: true,

    multipart_params : {
        "csrfmiddlewaretoken" : getCookie('csrftoken')
    },


    preinit: {
        'Init' : function(){
            // $('.plupload_header_title').text('Upload de Arquivos');
            $('.plupload_header_text').text('');
            // $('.plupload_buttons .plupload_add').text('Adicionar Arquivos');
            // $('.plupload_buttons .plupload_start').text('Iniciar Upload');
        },
        FilesAdded: function(up, files) {
            var max = up.settings.max_file_count;
            if ((up.files.length + files.length) > max){
                errorMessage('Max number of files: ' + max);
            }
        },
        QueueChanged: function(up){
            if (up.files.length > up.settings.max_file_count){
                while(up.files.length > up.settings.max_file_count){
                    up.removeFile(up.files[up.settings.max_file_count]);
                }
            }
        },
        FileUploaded: function(up, file, response) {
            var resp = JSON.parse(response.response);
            add_file(resp);
        }
    }

});

// Client side form validation
$('form').submit(function(e) {
//     var uploader = $('#uploader').pluploadQueue();
    $('#id_files_ids_list').val(get_files_list());

//     // Files in queue upload them first
//     if (uploader.files.length > 0) {
//         // When all files are uploaded submit form
//         uploader.bind('StateChanged', function() {
//             if (uploader.files.length === (uploader.total.uploaded + uploader.total.failed)) {
//                 $('form')[0].submit();
//             }
//         });

//         uploader.start();

//     } /*else {
//         errorMessage('You must queue at least one file.');
//     }*/
//     // return false;
});
});
