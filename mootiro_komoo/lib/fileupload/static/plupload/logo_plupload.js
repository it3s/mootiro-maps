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

    var addThumb = function(img){
        $('#logo-cat-thumbs-list').append(
            '<div class="file-entry logo-entry" org-category="' + img.id + '">' +
                '<img src="/static/' + img.filename + '" alt="img" class="logo-thumb">' +
            '</div>'
        );
    };

    var retrieveLogoCategoryImages = function(id_list){
        var id_list = id_list || [];
        var request_data = {
            'categories_list': id_list.join('|'),
            'bla': 'blee'
        };
        $.get(
            '/organization/category_images/',
            request_data,
            function(data){
                $('#logo-cat-thumbs-list').html('');
                if (data.images){
                    $.each(data.images, function(idx, img){
                        addThumb(img);
                    });
                    var id_logo_cat = $('#id_logo_category');  
                    if (id_logo_cat.val() && $('.logo-entry[org-category=' + id_logo_cat.val() + ']').length ){
                        $('.logo-entry[org-category=' + id_logo_cat.val() + ']').addClass('choosen');
                    } else {
                        var logo_cat= $('.logo-entry').first();
                        logo_cat.addClass('choosen');
                        $('#id_logo_category').val(logo_cat.attr('org-category'));
                    }
                }
            },
            'json'
        );
    }

    var updateCategoriesList = function() {
        var categories_list = [];
        $('#div_id_categories input[type=checkbox]:checked').each(function(i,o){
            categories_list.push($(this).val());
        });

        retrieveLogoCategoryImages(categories_list);
    }

    $('#div_id_categories input').click(function(){
        updateCategoriesList();
    });

});

