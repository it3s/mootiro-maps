/*
 * jQuery File Upload Plugin JS Example 5.0.2
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://creativecommons.org/licenses/MIT/
 */

/*jslint nomen: true */
/*global $ */
getFilesIdList = function(){
    var ids_list = [];
    $('#fileupload table.files tr').each(
        function(idx, item){
            var id = $(item).attr('file-id');
            ids_list.push(id);
        }
    );
    return ids_list;
};

$(function () {
    'use strict';

    var settings = {
        maxNumberOfFiles : 10,
        maxFileSize: 5000000,
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
    };

    $.extend(settings, upload_settings);

    $('#fileupload').fileupload({
        // autoUpload: true,
        maxNumberOfFiles: settings.maxNumberOfFiles,
        maxFileSize: settings.maxFileSize,
        acceptFileTypes: settings.acceptFileTypes
    });

    if (settings.fileuploaddone){
        $('#fileupload').bind('fileuploaddone', settings.fileuploaddone);
    }
    if (settings.fileuploaddone){
        $('#fileupload').bind('fileuploaddestroy', settings.fileuploaddestroy);
    }

    // Load existing files:
    $.getJSON($('#fileupload form').prop('action'), function (files) {
        var fu = $('#fileupload').data('fileupload');
        fu._adjustMaxNumberOfFiles(-files.length);
        fu._renderDownload(files)
            .appendTo($('#fileupload .files'))
            .fadeIn(function () {
                // Fix for IE7 and lower:
                $(this).show();
            });
    });

    // Open download dialogs via iframes,
    // to prevent aborting current uploads:
    $('#fileupload .files a:not([target^=_blank])').live('click', function (e) {
        e.preventDefault();
        $('<iframe style="display:none;"></iframe>')
            .prop('src', this.href)
            .appendTo('body');
    });

    $('.delete button').live('click', function(evt){
        var that = $(evt.target);
        that.parent().parent().fadeOut(400, function(){
            $(this).remove();
        });
    });
});
