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
$("#filter-slider-container .icon-remove").on("click", function () {
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

$(".needs div.img-holder").on("click", function (event) {
    //$(".need.categories ul img")
});


$("#filter-form").on("submit", function (event) {
    event.preventDefault();

    var url = dutils.urls.resolve('radial_search');
    var data = $("#filter-form").serialize();

    $.ajax({
        type: 'GET',
        url: dutils.urls.resolve('radial_search'),
        data: data
    }).success(function (data) {
        console.log(data);
    });

    return false;
});
