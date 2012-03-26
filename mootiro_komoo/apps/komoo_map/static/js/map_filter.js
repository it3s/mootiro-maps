// Add center functionality
$("#set-center").click(function () {
    editor.selectCenter(function (latLng, circle) {
        $("#filter-center").val(latLng.toUrlValue());
        $("#filter-radius").on("change", function () {
            var radius = parseInt($(this).val());
            circle.setRadius(radius);
        });
    });
});


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
