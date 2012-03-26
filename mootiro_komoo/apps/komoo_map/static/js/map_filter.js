
// Add center functionality
$("#set-center").click(function () {
    editor.selectCenter(function (latLng, circle) {
        console.log($("#filter-center"));
        $("#filter-center").val(latLng.toUrlValue());
        $("#filter-radius").on("change", function () {
            var radius = parseInt($(this).val());
            circle.setRadius(radius);
        });
    });
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
