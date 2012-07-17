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
function localStorageSet(key, obj){
    window.localStorage.setItem(key, JSON.stringify(obj));
}
function localStorageGet(key){
    return JSON.parse(window.localStorage.getItem(key));
}
function localStorageRemove(key){
    window.localStorage.removeItem(key);
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

// Add csrf token to ajax requests
jQuery(document).ajaxSend(function(event, xhr, settings) {
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

/* Easy to use, jQuery based, and elegant solution for tabs :) */
Tabs = function (tabs, contents, onChange, selectedClass) {
    this.tabs = tabs;
    this.contents = contents;
    this.selectedClass = selectedClass || "selected";
    this.onChange = onChange || function (instance) {};
    $(contents).hide();
    var instance = this;
    $(tabs).click(function () {
        instance.to(this);
        return false; // in order not to follow the link
    });
    // first shown tab is the first matched element in DOM tree
    this.length = $(tabs).length;
    this.to($(tabs)[0]);
    this.initialized = true;
};
Tabs.prototype.to = function (tab) { // Most important method, switches to a tab.
    $(this.tabs).removeClass(this.selectedClass);
    $(this.contents).removeClass(this.selectedClass).hide();

    var tab_content = $(tab).attr("href") || $(tab).children().attr("href");
    $("*[href=" + tab_content + "]").parent().addClass(this.selectedClass);
    $(tab_content).addClass(this.selectedClass).show();

    this.current = tab;
    if (this.onChange && this.initialized) {
        this.onChange(this);
    }
};
Tabs.prototype.getCurrentTabIndex = function () {
    return $(this.tabs).index(this.current);
};


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
 *  jQuery plugin for Field description boxes
 *  Usage:
 *  $('#form_resource').komooFormHintBoxes({
 *      'name': {
 *          desc: 'bla name bla name bla'
 *      },
 *      'kind': {
 *          left: '640px',
 *          top: '40%',
 *          desc: 'blbalablba kind lnakslka'
 *      }
 *  });
 *
 */
 (function($){
    $.fn.komooFormHintBoxes = function(box_config){
        var defaults = {
            left: '740px',
            top: '-2px'
        }
        var form = $(this);

        var hintBoxesFocusCb = function(el){
            var el = $(el);
            var node, i;
            for ( node = el, i = 0;
                  (!$(node).is('.control-group')) && i < 15;
                  node = node.parent(), i++
            );

            // remove focus from previous element
            $('.control-group.focus').each(function(idx, obj){
                var obj = $(obj);
                if(!obj.is(el)){
                    obj.removeClass('focus');
                    obj.find('.field-hint-box-wrapper').hide();
                }
            });

            if (node.is('.control-group') && !node.is('.focus')){
                node.addClass('focus');
                node.find('.field-hint-box-wrapper').show();
            }
        };

        $(function(){
            $('.field-hint-box-wrapper').hide();
        });


        $('input, textarea').live('focus',function(){
            hintBoxesFocusCb(this);
        });

        // this is ugly and very dependant on how django/crispyforms
        // generates our . But its quick and works.
        // Perhaps we should refactor this latter
        $('#div_id_files, #div_id_logo, .org-widget-categories, #div_id_categories').live(
            'click',
            function(){
                hintBoxesFocusCb(this);
            }
        );
        // $('#div_id_files').live('blur', function(){
        //     var el = $(this);
        //     el.removeClass('focus');
        //     el.find('.field-hint-box-wrapper').fadeOut('fast');
        // });

        $.each(box_config, function(key, val){
            var el = form.find('#div_id_' + key);
            el.find('.controls').append("" +
                "<div class='field-hint-box-wrapper'>" +
                    "<span class='hint-box-line'>&nbsp;&nbsp;</span>" +
                    "<div class='field-hint-box'>" +
                    "<img class='hint-icon' src='/static/img/hint-icon.png' >" +
                    "<div class='hint-text'>" + val.hint  + "</div>" +
                    "</div>" +
                "</div>"
            );

            var conf = {}
            $.extend(conf, defaults, val);

            el.find('.field-hint-box-wrapper'
              ).css('left', conf.left).css('top', conf.top);
            if (conf.width){
                el.find('.field-hint-box-wrapper').css('width', conf.width + 30);
                el.find('.field-hint-box').css('width', conf.width);
            }
        });

        // form.find('fieldset').after("" +
        //     "<div class='alert alert-info' data-alert='info'>" +
        //         "<a class='close' data-dismiss='alert'>×</a>" +
        //         "<div class='msg'>" +
        //             "Os campos com asterisco (<strong>*</strong>) são obrigatórios!" +
        //         "</div>" +
        //     "</div>"
        // );

        $('.close').click(function(){
            $(this).parent().fadeOut();
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
    // Intercepts all links that have the class /login-required/
    $("a.login-required").bind("click.loginrequierd", function (ev) {
        if (!isAuthenticated) {
            // TODO: request status from server
            ev.stopPropagation();
            ev.stopImmediatePropagation();
            ev.preventDefault();
            var url = $(this).attr("href");
            if (url == "/vote/add/") {
                url = document.location.pathname;
            } else if (url.charAt(0) == "#") {
                url = document.location.pathname + url;
            }
            $("#login-box #login-button").attr("href", "/user/login?next=" + encodeURIComponent(url));
            $("#login-box").dialog({
                width: 850,
                modal: true,
                resizable: false,
                draggable: false
            });
            return false;
        }
    });
});

function _displayMessage(selector, dialogClass, title, message, imageUrl, buttons) {
    if (!buttons) {
        buttons = [
            {
                text: "Ok",
                'class': "button",
                click: function () { $(this).dialog("close"); }
            }
        ];
    }
    var $box = selector;
    $(".message", $box).text(message);
    $box.dialog({
        dialogClass: dialogClass,
        title: title,
        modal: true,
        buttons: buttons,
        resizable: false,
        draggable: false,
        width: 400
    });
    return $box;
}

function errorMessage(title, message, imageUrl, buttons) {
    return _displayMessage($("#error-box"), "error-dialog",
            title, message, imageUrl, buttons);
}

function infoMessage(title, message, imageUrl, buttons) {
    return _displayMessage($("#info-box"), "info-dialog",
            title, message, imageUrl, buttons);
}

function confirmationMessage(title, message, imageUrl, callback) {
    buttons = [
        {
            text: gettext("Yes"),
            'class': "btn",
            click: function () { callback("yes"); $(this).dialog("close"); }
        },
        {
            text: gettext("No"),
            'class': "button",
            click: function () { callback("no"); $(this).dialog("close"); }
        }
    ];
    return infoMessage(title, message, imageUrl, buttons);
}

function unexpectedError(info) {
    //TODO: translate me!
    title = "Ops!";
    message = "O Spock comeu um pedaço do código... Nos escreva falando que problema você encontrou para que possamos resolvê-lo!";
    buttons = [];

    var $box = $("#unexpected-error-box");
    $(".message", $box).text(message);
    $("input[name=url]").val(location.href);
    $("input[name=info]").val(info || "");
    $box.dialog({
        dialogClass: "error-dialog unexpected-error-dialog",
        title: title,
        modal: true,
        buttons: buttons,
        resizable: false,
        draggable: false,
        width: 650
    });
    return $box;
}

function flash(message, optDuration) {
    var duration = optDuration || 10000;
    var $box = $("#flash-message");
    $(".message", $box).text(message);
    $box.show();
    if (duration > 0)
        setTimeout(function () { $box.fadeOut(); }, duration);
}

/* Komoo style tooltips. Based on bootstrap tooltip plugin. */
(function($){
    $.fn.komooTooltip = function() {
        var $target = $(this);
        $target.tooltip({
            placement: "bottom",
            trigger: "manual"
        }).on("click", function (evt) {
            $target = $(evt.target);
            $target.tooltip('show');
            $(".tooltip").on("mouseleave", function (evt) {
                $target.tooltip('hide');
            });
        });
    };
})(jQuery);
