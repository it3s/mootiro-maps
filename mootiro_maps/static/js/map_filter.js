/******* Center *******/
$("#set-center").click(function () {
    editor.selectCenter(parseInt($("#filter-radius").val()), function (latLng, circle) {
        $("#filter-center").val(latLng.toUrlValue()).change();
        $("#filter-radius").on("change", function () {
            var radius = parseInt($(this).val());
            circle.setRadius(radius);
        });
        $("#filter-helper").hide();
        $("#filter-radius").focus();
    });
    $("#filter-slider-container").hide();
    $("#filter-radius").parent().removeClass("highlight");
    $("#filter-helper").show();
});

/******* Slider *******/
$("#filter-slider").slider({
    range: "min",
    min: 100,
    max: 10000,
    value: 1000,
    slide: function( event, ui ) {
        $("#filter-radius").val(ui.value).trigger("change");
    }
});
$("#filter-radius").val($("#filter-slider").slider("value"));
$("#filter-radius").on("change", function () {
    // handles value consistence between slider and input field
    var old_value = $("#filter-slider").slider("value");
    var new_value = parseInt($(this).val());
    var min = $("#filter-slider").slider("option", "min");
    var max = $("#filter-slider").slider("option", "max");

    if (isNaN(new_value)) {
        new_value = old_value;
    } else if (new_value < min) {
        new_value = min;
    } else if (new_value > max) {
        new_value = max;
    }
    $("#filter-radius").val(new_value);
    $("#filter-slider").slider("value", new_value);
});
$("#filter-radius").focus(function () {
    $("#filter-slider-container").show();
    $("#filter-radius").parent().addClass("highlight");
});
$("#filter-slider-container .icon-ok").on("click", function () {
    $("#filter-slider-container").hide();
    $("#filter-radius").parent().removeClass("highlight");
});

/******* Navigation *******/
$("#filter-back, #filter-results .icon-remove").live("click", function (event) {
    $("#filter-results-container").hide();
    $("#filter-form").show();
});

/******* Form submission *******/
function checkFilterFormIsReady (event) {
    var $form = $("#filter-form");
    var center_ok = Boolean($("#filter-center", $form).val());
    var objs_ok = Boolean($(".geo-objects-listing input", $form).serialize());
    var filter_ready = center_ok && objs_ok;
    if (filter_ready) {
        $("#filter-submit").addClass("button").removeClass("button-off");
    } else {
        $("#filter-submit").addClass("button-off").removeClass("button");
    };
    return false;
};
$("#filter-center").on("change", checkFilterFormIsReady);
$("#filter-form ul.geo-objects-listing").on("click", checkFilterFormIsReady);

$("#filter-form").on("submit", function (event) {
    event.preventDefault();
    var $form = $("#filter-form");

    // do not submit if parameters are not ready
    if ($("#filter-submit", $form).hasClass("button-off"))
        return false;

    var need_categories = $("input[name=need_categories]").serializeArray()
        .map(function (item) {
            return item.value;
        }).join(',');

    var data = ""
    data += $("input[name=center], input[name=radius], " +
              "input[name=communities], input[name=needs], " +
              "input[name=organizations], input[name=resources]", $form).serialize();
    data += "&need_categories=" + need_categories;

    var url = dutils.urls.resolve('radial_search');

    $.ajax({
        type: 'GET',
        url: dutils.urls.resolve('radial_search'),
        data: data
    }).success(function (html) {
        $("#filter-form").hide();
        $("#filter-results-container").show();
        $("#filter-results").html(html);
    });
    return false;
});

/******* Results viewing *******/
$("#filter-results .sublist ul li").live("mouseover", function (event) {
    var obj_id = parseInt($(this).attr("id").match(/[0-9]+$/)[0]);
    obj_id = parseInt(obj_id);
    var obj_type = $(this).attr("id").match(/^(.+)-/)[1];
    editor.highlightFeature(obj_type, obj_id);
});

/******* Configure geo objects listing behaviours *******/
$(function () {
    // Lines below must be after checkFilterFormIsReady() callback registering
    geoObjectsListing("#map-panel-filter ul.geo-objects-listing");
    geoObjectsListing("#map-panel-layers ul.geo-objects-listing");
    geoObjectsListing("#map-panel-add ul.geo-objects-listing");
});

/******* Layers *******/
// Starts with all layers checked
$("#map-panel-layers div.img-holder > img").trigger("click");
$("#map-panel-layers div.img-holder input[type=checkbox]").attr("checked", "checked");
$("#map-panel-layers .need.sublist").hide();

$("#map-panel-layers > ul > li:not(.needs) div.img-holder > img").bind("click", function () {
    alert
    var $this = $(this);
    var $parent = $this.parent();
    var objectType = $parent.attr("data-object-type");

    if (objectType) {
        if ($("input[type=checkbox]", $parent).attr("checked")) {
            editor.showFeaturesByType(objectType);
        } else {
            editor.hideFeaturesByType(objectType);
        }
    }
});

$("#map-panel-layers > ul > li.sublist > ul > li > div.img-holder > img").bind("click", function () {
    var $this = $(this);
    var $parent = $this.parent();
    var objectType = "Need";
    var category = $parent.attr("data-original-label");
    var enabledCategories = ['uncategorized'];
    $.each($("input:checked", $parent.parent().parent()).parent(), function (key, element) {
        var e = $(element);
        if (e) {
            enabledCategories.push(e.attr("data-original-label"));
        }
    });

    if ($("input[type=checkbox]", $parent).attr("checked")) {
        editor.showFeaturesByType(objectType, [category]);
    } else {
        editor.hideFeaturesByType(objectType, [category]);
    }

    if (enabledCategories.length == 1)
        editor.hideFeaturesByType(objectType, ['uncategorized']);
    else
        editor.showFeaturesByType(objectType, enabledCategories);
});

/******* Add *******/
$("#map-panel-add .sublist").hide();
$(function () {
    var items = $("#map-panel-add .geo-objects-listing > li");
    $.each(items, function (i, item) {
        var $item = $(item);
        var type = $item.attr("data-object-type");
        var geometryType = $item.attr("data-geometry-type");
        if (geometryType) {
            // console.log(type, geometryType);
        }
        if ($item.hasClass("sublist")) {
            var subitems = $(".add", $item);
            $.each(subitems, function (i, subitem) {
                var $subitem = $(subitem);
                var geometryType = $subitem.attr("data-geometry-type");
                $subitem.click(function (e) {
                    if (editor.addPanel.is(":visible")){
                        return;
                    }
                    editor.setDrawingMode(type, geometryType);
                    $("#map-panel-add .selected").removeClass("selected");
                    $subitem.addClass("selected");

                });
            });
        }
    });
});
