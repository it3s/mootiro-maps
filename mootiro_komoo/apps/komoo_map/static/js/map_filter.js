/* Add center functionality */
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

/* Slider configuration */
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

// $(".geo-objects-listing li div.img-holder").on('click', function (event) {
//     event.preventDefault();
// });
// $(".geo-objects-listing li").bind('click', function () {
//     alert("li");
//     // triggerHandler does not bubble the event
//     var $img = $("img", this)
//     console.log($img);
//     var v = $img.triggerHandler('click');
//     alert(v);
//     return false;
// });

function hierarchicalImageSwitchSelection (parent, children) {
    var $parent = $(parent);
    var $parent_img = $("#tick_img_" + $parent.attr("id"));

    var $children = $(children);

    $parent_img.on("click", function (event) {
        var parent_status = Boolean($parent.attr('checked'));

        $children.each(function (index, child) {
            var $child = $(child);
            var $child_img = $("#tick_img_" + $child.attr("id"));
            var status = Boolean($child.attr('checked'));

            if (status != parent_status) {
                $child_img.click();
            }
        });

    });
}

hierarchicalImageSwitchSelection("#id_needs", "input[name=need_categories]");

$(".needs div.img-holder").on("click", function (event) {
    var $sub_checkboxes = $();
    //$(".need.categories ul img")
});

$("#filter-back, #filter-results .icon-remove").live("click", function (event) {
    $("#filter-results-container").hide();
    $("#filter-form").show();
});

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
    data += "&need_categories=" +need_categories;

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

// $(function () {
//     $("#filter-form input[type=checkbox]").attr('checked', true);
//     $("#filter-center").val("-23.561233,-46.74922");
//     $("#filter-form").submit();
// });
