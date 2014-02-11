$(function() {
    $('#add-to-project').click(function(evt){
        var el = $(evt.target);
        if (isAuthenticated && !el.is('.disabled')){
          $('#add-project-modal').modal('show');
        }
        return false;
    });
    $( "#id_project_autocomplete" ).bind( "autocompleteselect", function(event, ui) {
        $('.add-project-msg').html(
            '<p>' +
                gettext('This list will be added to the project') +
                ' <strong>' +  ui.item.label + '</strong> ' +
            '</p>'
        );
    });
    var cleanAddToProjectFields = function() {
        $('#id_project_autocomplete').val('');
        $('#id_project').val('');
        $('.add-project-msg').html('');
        $('#add-project-modal').modal('hide');
    };
    $('#add-project-save').click(function(){
        //save proj related object
        var project_id = $('#id_project').val();
        $.post(
            '/project/add_list/',
            {
                filter_params: $('#add_to_project__filter_params').val(),
                object_type: $('#add_to_project__object_type').val(),
                project_id: project_id
            },
            function(data){
                if (data.success) {
                    // redirect to project page
                    window.location.href = data.redirect_url;
                } else {
                    alert(gettext('Failed to relate this list to the selected project'));
                }
            },
            'json'
        );
        $('#id_project_autocomplete').val('');
        $('#id_project').val('');
        $('.add-project-msg').html('');
        $('#add-project-modal').modal('hide');
    });
    $('#add-project-cancel').click(function(evt){
        evt.preventDefault();
        cleanAddToProjectFields();
        return false;
    });

});
