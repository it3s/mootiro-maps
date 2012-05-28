$(function () {
    var dialog;

    function getReportContentBox(button) {
        // Get the report box code using ajax
        $.ajax({
            url: dutils.urls.resolve("report_content_box"),
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
                    var serialized = $(this).serialize();
                    $.ajax({
                        url: $(this).attr("action"),
                        cache: false,
                        data: serialized,
                        dataType: "json",
                        type: "POST",

                        success: function (data, textStatus, jqXHR) {
                            if (data.error) {
                                errorMessage(gettext("Error"), data.error);
                            } else {
                                // TODO Show feedback message
                                dialog.dialog("close");
                            }
                        },

                        error: function (jqXHR, textStatus, errorThrown) {
                            errorMessage(gettext("Error"),
                                gettext("An error occurred, please try again later."));
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
                errorMessage(gettext("Network error"),
                    gettext("An error occurred while connecting to network!"));
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

    openDeleteContentDialog = function (button) {
        var appLabel = button.attr("data-app-label");
        var modelName = button.attr("data-model-name");
        var objectId = button.attr("data-id");
        $.ajax({
            type: 'POST',
            url: dutils.urls.resolve("moderation_delete", {
                app_label: appLabel,
                model_name: modelName,
                obj_id: objectId
            }),
            success: function (data, textStatus, jqXHR) {
                errorMessage("Enviado");
            }
        });
    };

    // Connect all delete buttons
    var deleteButtons = $(".delete-content-btn");
    $.each(deleteButtons, function (key, btn) {
        var button = $(btn);
        button.bind("click", function (ev) {
            openDeleteContentDialog (button);
            return false;
        });
    });

});
