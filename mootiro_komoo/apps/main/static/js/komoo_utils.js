/*
 * Utilitary functions for working with session storage
 */
function storageSet(key, obj){
    window.sessionStorage.setItem(key, JSON.stringify(obj));
}
function storageGet(key){
    return JSON.parse(window.sessionStorage.getItem(key));
}
function storageRemove(key){
    window.sessionStorage.removeItem(key);
}

/* function for getting xsrf cookies */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* Easy to use, jQuery based, and elegant solution for tabs :) */
function Tabs(tabs, contents, onChange) {
    $(contents).hide();
    var instance = this;
    this.to = function (tab) { // Most important method, switches to a tab.
        $(tabs).removeClass("selected");
        $(contents).removeClass("selected").hide();

        var tab_content = $(tab).attr("href") || $(tab).children().attr("href");
        $("*[href=" + tab_content + "]").parent().addClass("selected");
        $(tab_content).addClass("selected").show();

        instance.current = tab;
        if (onChange && instance.initialized) {
            onChange(instance);
        }
    };
    this.getCurrentTabIndex = function () {
        return $(tabs).index(instance.current);
    };
    $(tabs).click(function () {
        instance.to(this);
        return false; // in order not to follow the link
    });
    // first shown tab is the first matched element in DOM tree
    this.length = $(tabs).length;
    this.to($(tabs)[0]);
    this.initialized = true;
}


/*
 * retrieve params from url
 */
function getUrlVars(){
    var vars = [], hash;
    var hashes = window.location.href.slice(
        window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

/*
 * jQuery plugin for clearing forms
 * usage:
 *    jQuery('#meu_form').clearForm();
 *
 */
(function($){
    $.fn.clearForm = function() {
        return this.each(function() {
            var type = this.type, tag = this.tagName.toLowerCase();
            if (tag == 'form'){
                return $(':input',this).clearForm();
            }
            if (type == 'text' || type == 'password' || tag == 'textarea'){
                jQuery(this).val('');
            }
            else if(type == 'hidden' && this.name !== "csrfmiddlewaretoken"){
                jQuery(this).val('');
            }
            else if (type == 'checkbox' || type == 'radio'){
                jQuery(this).attr('checked', false);
            }
            else if (tag == 'select'){
                jQuery(this).val('');
            }
        });
    };
})(jQuery);


/*
 * Configure behaviour of geo objects listing
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
            if (status($parent) === false) {
                // save selected children
                $selectedChildren = $children.filter(function (index) {
                    return status(this);
                });
            }
            $.each($selectedChildren, function (index, child) {
                $(child).click();
            });
        }
    });
    $("div.img-holder, .collapser", $parent).on('click', function (event) {
        return false; // prevent event bubbling
    });

    if (children) {
        var $children = $(children);
        var $selectedChildren = $children; // starts manipulating all subitems

        /* Children setup */
        $children.on("click", function (event) {
            $("div.img-holder img", $(this)).trigger("click");

            /* Parent behaviour related to children */
            var numSelectedChildrens = $children.filter(function (index) {
                    return status(this);
                }).length;
            if (numSelectedChildrens === 0) {
                status($parent, false);
            } else {
                status($parent, true);
            }
        });
        $("div.img-holder, .collapser", $children).on('click', function (event) {
            return false; // prevent event bubbling
        });
    }
}
function geoObjectsListing (ul) {
    var $ul = $(ul);

    /* Setup collapsers */
    $(".collapser", $ul).on("click", function (event) {
        var $this = $(this);
        $("i", $this).toggleClass("icon-chevron-right icon-chevron-down");
        $this.parent().next().toggle();
    });

    /* Setup behaviour */
    geoObjectsSelection($("li.communities", $ul));
    geoObjectsSelection($("li.needs", $ul), $("li.need.sublist ul li", $ul));
    geoObjectsSelection($("li.organizations", $ul));
    geoObjectsSelection($("li.resources", $ul));

}

$(function () {
    // Intercepts all links that have the class /authenticate/
    $("a.login-required").click(function (ev) {
        if (!isAuthenticated) {
            // TODO: request status from server
            var url = $(this).attr("href");
            if (url == "/vote/add/") {
                url = document.location.pathname;
            } else if (url.charAt(0) == "#") {
                url = document.location.pathname + url;
            }
            $("#login-box #login-button").attr("href", "/user/login?next=" + url);
            $("#login-box").dialog({
                width: 850,
                modal: true,
                resizable: false,
                draggable: false
            });
            ev.stopPropagation();
            return false;
        }
    });
});

function errorMessage(title, message, imageUrl, buttons) {
    if (!buttons) {
        buttons = [
            {
                text: "Ok",
                'class': "button",
                click: function() { $(this).dialog("close"); }
            }
        ];
    }
    var box = $("#error-box");
    $(".message", box).text(message);
    box.dialog({
        dialogClass: "error-dialog",
        title: title,
        modal: true,
        buttons: buttons,
        resizable: false,
        draggable: false,
        width: 400
    });
    return box;
}

function unexpectedError(info) {
    title = "Ops!";
    message = "O Spock comeu um pedaço do código... Nos escreva falando que problema você encontrou para que possamos resolvê-lo!";
    buttons = [];

    var box = $("#unexpected-error-box");
    $(".message", box).text(message);
    $("input[name=url]").val(location.href);
    $("input[name=info]").val(info || "");
    box.dialog({
        dialogClass: "error-dialog unexpected-error-dialog",
        title: title,
        modal: true,
        buttons: buttons,
        resizable: false,
        draggable: false,
        width: 650
    });
    return box;
}
