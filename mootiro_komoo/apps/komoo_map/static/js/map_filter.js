/******* Configure geo objects listing behaviours *******/
$(function () {
    geoObjectsListing("#map-panel-filter ul.geo-objects-listing");
    geoObjectsListing("#map-panel-layers ul.geo-objects-listing");
    geoObjectsListing("#map-panel-add ul.geo-objects-listing");
});

/******* Center *******/
$("#set-center").click(function () {
    editor.selectCenter(parseInt($("#filter-radius").val()), function (latLng, circle) {
        $("#filter-center").val(latLng.toUrlValue());
        $("#filter-radius").on("change", function () {
            var radius = parseInt($(this).val());
            circle.setRadius(radius);
        });
        $("#filter-helper").hide();
        $("#filter-radius").focus();
    });
    $("#filter-slider-container").hide();
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
});
$("#filter-slider-container .icon-ok").on("click", function () {
    $("#filter-slider-container").hide();
});

/******* Navigation *******/
$("#filter-back, #filter-results .icon-remove").live("click", function (event) {
    $("#filter-results-container").hide();
    $("#filter-form").show();
});

/******* Form submission *******/
$("#filter-form").on("submit", function (event) {
    event.preventDefault();

    var $form = $("#filter-form");
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
    editor.highlightOverlay(obj_type, obj_id);
});

// $(function () {
//     $("#filter-form input[type=checkbox]").attr('checked', true);
//     $("#filter-center").val("-23.561233,-46.74922");
//     $("#filter-form").submit();
// });

/******* Layers *******/
// Starts with all layers checked
$("#map-panel-layers div.img-holder > img").trigger("click");
$("#map-panel-layers div.img-holder input[type=checkbox]").attr("checked", "checked");
$("#map-panel-layers .need.sublist").hide();

$("#map-panel-layers > ul > li:not(.needs) > div.img-holder > img").bind("click", function () {
    var $this = $(this);
    var $parent = $this.parent();
    var objectType = $parent.attr("data-object-type");

    if (objectType) {
        if ($("input[type=checkbox]", $parent).attr("checked")) {
            editor.showOverlaysByType(objectType);
        } else {
            editor.hideOverlaysByType(objectType);
        }
    }
});

$("#map-panel-layers > ul > li.sublist > ul > li > div.img-holder > img").bind("click", function () {
    var $this = $(this);
    var $parent = $this.parent();
    var objectType = "need";
    var category = $parent.attr("data-original-label");
    var enabledCategories = [];
    $.each($("input:checked", $parent.parent().parent()).parent(), function (key, element) {
        var e = $(element);
        if (e) {
            enabledCategories.push(e.attr("data-original-label"));
        }
    });

    if ($("input[type=checkbox]", $parent).attr("checked")) {
        editor.showOverlaysByType(objectType, [category]);
    } else {
        editor.hideOverlaysByType(objectType, [category]);
    }

    editor.showOverlaysByType(objectType, enabledCategories);
});

/******* Add *******/
$("#map-panel-add .sublist").hide();
$(function () {
    var items = $("#map-panel-add .geo-objects-listing > li");
    $.each(items, function (i, item) {
        var $item = $(item);
        var type = $item.attr("data-object-type");
        var overlayType = $item.attr("data-overlay-type");
        if (overlayType) {
            console.log(type, overlayType);
        }
        if ($item.hasClass("sublist")) {
            var subitems = $(".add", $item);
            $.each(subitems, function (i, subitem) {
                var $subitem = $(subitem);
                var overlayType = $subitem.attr("data-overlay-type");
                console.log(type, overlayType);
                $subitem.click(function (e) {
                    if (editor.addPanel.is(":visible")){
                        return;
                    }
                    editor.setDrawingMode(type, overlayType);
                    $("#map-panel-add .selected").removeClass("selected");
                    $subitem.addClass("selected");

                });
            });
        }
    });
});

/******* Collapse *******/
$("#collapse-panel").click(function (ev) {
    $("#map-container-main, #map-container-editor").toggleClass("collapsed");
    google.maps.event.trigger(editor.googleMap, 'resize');
    var interval = setInterval("google.maps.event.trigger(editor.googleMap, 'resize');", 500)
    setTimeout(function () { clearInterval(interval); }, 1000)
});
