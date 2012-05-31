$(function () {
    var scriptFile = "moderation.js";

    var dialog;

    function getReportContentBox(button) {
        // Get the report box code using ajax
        var url = dutils.urls.resolve("report_content_box");
        $.ajax({
            url: url,
            context: $("#root"),

            success: function (data, textStatus, jqXHR) {
                $(this).append($(data));
                var form = $("#report-content-form");
                form.submit(function (ev) {
                    // Verify if the required field was filled
                    if (!$("input[type=radio]:checked", form).val()) {
                        var radioContainer = $("#report-content-radio-container");
                        radioContainer.addClass("error");
                        $("input[type=radio]", form).change(function (ev) {
                            radioContainer.removeClass("error");
                        });
                        return false;
                    }

                    // Send the form using ajax
                    var url = $(this).attr("action");
                    var postData = $(this).serialize();
                    $.ajax({
                        url: url,
                        cache: false,
                        data: postData,
                        dataType: "json",
                        type: "POST",

                        success: function (data, textStatus, jqXHR) {
                            if (data.error) {
                                var info = JSON.stringify({
                                    script: scriptFile,
                                    reference: "getReportContentBox#responseError",
                                    info: "An error occurred while trying to report a content.",
                                    ajaxUrl: url,
                                    ajaxPostData: postData,
                                    jqXHR: jqXHR
                                });
                                unexpectedError(info);
                            } else {
                                flash(data.message);
                                dialog.dialog("close");
                            }
                        },

                        error: function (jqXHR, textStatus, errorThrown) {
                            var info = JSON.stringify({
                                script: scriptFile,
                                reference: "getReportContentBox#ajaxError",
                                info: "An error occurred while trying to report a content.",
                                ajaxUrl: url,
                                ajaxPostData: postData,
                                jqXHR: jqXHR
                            });
                            unexpectedError(info);
                        }
                    });
                    return false;
                });
                // Cancel button
                $("#report-content-cancel-btn").click(function (ev) {
                    dialog.dialog("close");
                    form.clearForm();
                    return false;
                });
                openReportContentDialog(button, true);
            },

            error: function (jqXHR, textStatus, errorThrown) {
                var info = JSON.stringify({
                    script: scriptFile,
                    reference: "getReportContentBox#ajaxError",
                    info: "An error occurred while trying to get the abuse report form.",
                    ajaxUrl: url,
                    ajaxPostData: "none",
                    jqXHR: jqXHR
                });
                unexpectedError(info);
            }
        });

    }

    openReportContentDialog = function (button, avoidInfiniteLoop) {
        var box = $("#report-content-box");
        // Get the object info
        var appLabel = button.attr("data-app-label");
        var modelName = button.attr("data-model-name");
        var objectId = button.attr("data-id");
        if (box.length != 0) {
            // Set the form action url
            $("#report-content-form").attr({
                action: dutils.urls.resolve("moderation_report", {
                    app_label: appLabel,
                    model_name: modelName,
                    obj_id: objectId
                })
            });
            // Open the form
            var form = $("#report-content-form");
            form.clearForm();
            dialog = box.dialog({
                title: gettext("Report Abuse"),
                width: 450,
                modal: true,
                resizable: false,
                draggable: false
            });
        } else if (!avoidInfiniteLoop) {
            // Get the form using ajax
            getReportContentBox(button);
        }
    };

    // Connect all report buttons
    var reportButtons = $(".report-content-btn");
    $.each(reportButtons, function (key, btn) {
        var button = $(btn);
        button.bind("click", function (ev) {
            openReportContentDialog (button);
            return false;
        });
    });

    deleteContent = function (button, confirmed) {
        var appLabel = button.attr("data-app-label");
        var modelName = button.attr("data-model-name");
        var objectId = button.attr("data-id");

        var url = dutils.urls.resolve("moderation_delete", {
            app_label: appLabel,
            model_name: modelName,
            obj_id: objectId
        });
        var postData = { confirmed: (confirmed || false) };

        $.ajax({type: 'POST', url: url, data: postData,
            success: function (data, textStatus, jqXHR) {
                if (data.success == "true") {
                    if (data.next == "confirmation") {
                        confirmationMessage(gettext("Delete"),
                            gettext("Do you want to delete this content permanently?"),
                            "",
                            function (response) {
                                if (response == "yes") {
                                    deleteContent(button, true);
                                }
                            });
                    } else if (data.next == "request") {
                        //TODO
                        console.log("display request dialog");
                    } else if (data.next == "showDeleteFeedback") {
                        flash(gettext("The content was successfully deleted"), -1);
                        var $mainContent = $("#main-content");
                        $("#content").height($mainContent.height());
                        $mainContent.fadeOut();
                    } else if (data.next == "showRequestFeedback") {
                        flash(gettext("Deletion request sent"));
                    }
                } else {
                    var info = JSON.stringify({
                        script: scriptFile,
                        reference: "deleteContent#responseError",
                        info: "An error occurred while trying to delete a content.",
                        ajaxUrl: url,
                        ajaxPostData: postData,
                        jqXHR: jqXHR
                    });
                    unexpectedError(info);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                var info = JSON.stringify({
                    script: scriptFile,
                    reference: "deleteContent#ajaxError",
                    info: "An error occurred while trying to delete a content.",
                    ajaxUrl: url,
                    ajaxPostData: postData,
                    jqXHR: jqXHR
                });
                unexpectedError(info);
            }
        });
    };

    // Connect all delete buttons
    var deleteButtons = $(".delete-content-btn");
    $.each(deleteButtons, function (key, btn) {
        var button = $(btn);
        button.bind("click", function (ev) {
            deleteContent(button);
            return false;
        });
    });

});
