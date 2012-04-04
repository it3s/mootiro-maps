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

/******* List items behavior *******/
/**
 * Receives an element
 * parent is a <li>
 */
function geoObjectsSelection (parent, children) {
    var status = function (elem, value) {
        st = Boolean($("input", $(elem)).attr('checked'));
        if (value == undefined) return st;
        if (value != st)
            $("div.img-holder img", $(elem)).trigger("click");
        return value;
    };
    /* Parent setup */
    var $parent = $(parent);
    var $selectedChildren = [];
    $parent.on('click', function (event) {
        $("div.img-holder img", $(this)).trigger("click");

        /* Children behaviour related to parent */
        if (children) {
            if (status($parent) == false) {
                // save selected children
                $selectedChildren = $children.filter(function (index) {
                    return status(this);
                });
            };
            $.each($selectedChildren, function (index, child) {
                $(child).click();
            });
        };
    });
    $("div.img-holder, .collapser", $parent).on('click', function (event) {
        return false; // prevent event bubbling
    });

    if (children) {
        var $children = $(children);

        /* Children setup */
        $children.on("click", function (event) {
            $("div.img-holder img", $(this)).trigger("click");

            /* Parent behaviour related to children */
            var numSelectedChildrens = $children.filter(function (index) {
                    return status(this);
                }).length;
            if (numSelectedChildrens == 0) {
                status($parent, false);
            } else {
                status($parent, true);
            };
        });
        $("div.img-holder, .collapser", $children).on('click', function (event) {
            return false; // prevent event bubbling
        });
    }

};
geoObjectsSelection("#map-panel-filter li.communities");
geoObjectsSelection("#map-panel-filter li.needs", "li.need.sublist ul li");
geoObjectsSelection("#map-panel-filter li.organizations");
geoObjectsSelection("#map-panel-filter li.resources");

$(".geo-objects-listing .needs .collapser").on("click", function (event) {
    $(".need.sublist").toggle();
    $("i", this).toggleClass("icon-chevron-right icon-chevron-down");
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
