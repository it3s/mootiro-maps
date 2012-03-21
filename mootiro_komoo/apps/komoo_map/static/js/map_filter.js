
// Add center functionality
$("#filter-center").click(function () {
    alert("Não clique aí!");
});


$("#filter-form").on("submit", function (event) {
    event.preventDefault();

    var radius = $("#filter-radius");
    var center = "-23.56517,-46.773133";
    var url = dutils.urls.resolve('radial_search');
    
    $.ajax({
        type: 'GET',
        url: dutils.urls.resolve('radial_search'),
        data: {
            radius: radius,
            center: "-23.56517,-46.773133"
        }
    }).success(function (data) {
        console.log(data);
    });
    
    return false;
});
