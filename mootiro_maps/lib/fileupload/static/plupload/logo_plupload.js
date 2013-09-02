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
        $('#logo-thumb').html(
            '<img src="' + resp.url + '" >'
        );
        setLogoChoice('uploaded');
    });
    logo_uploader.bind('Error', function(up, err) {
        alert(err);
        up.refresh(); // Reposition Flash/Silverlight
    });

    var addThumb = function(img){
        $('#logo-cat-thumbs-list').append(
            '<div class="file-entry logo-entry" org-category="' + img.id + '">' +
                '<img src="/static/img/org_categories/' + img.filename + '" alt="img" class="logo-thumb">' +
            '</div>'
        );
    };

    var retrieveLogoCategoryImages = function(id_list){
        id_list = id_list || [];
        $('#logo-cat-thumbs-list').html('');
        if (id_list.length){
            $.each(id_list, function(idx, num){
                addThumb({
                    id: num,
                    filename: organization_category_images[num]
                });
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
    };

    var updateCategoriesList = function() {
        var categories_list = [];
        $('#div_id_categories input[type=checkbox]:checked').each(function(i,o){
            categories_list.push($(this).val());
        });

        retrieveLogoCategoryImages(categories_list);
    };

    var setLogoChoice = function(choice){
        var choice_vals = {
            'category': 'CAT',
            'uploaded': 'UP'
        };

        $('input[type="radio"][name=logo_type][value="' + choice +'"]').attr('checked', 'checked');
        $('#id_logo_choice').val(choice_vals[choice]);
    };

    $('#div_id_categories input').click(function(){
        updateCategoriesList();
    });

    updateCategoriesList();

    // fix radio button entries
    var logo_choice = $('#id_logo_choice');
    if( logo_choice.val()){
        var choice_vals = {
            'CAT': 'category',
            'UP': 'uploaded'
        };
        setLogoChoice(choice_vals[logo_choice.val()]);
    }

    $('input[name=logo_type]').click(function(){
        setLogoChoice($(this).val());
    });

    $('.logo-entry').live('click', function(){
        $('.logo-entry.choosen').removeClass('choosen');
        $(this).addClass('choosen');
        $('#id_logo_category').val($(this).attr('org-category'));

        setLogoChoice('category');
    });

});


