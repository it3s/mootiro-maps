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
function Tabs(tabs, contents) {
    $(contents).hide();
    var instance = this;
    this.to = function (tab) { // Most important method, switches to a tab.
        $(tabs).removeClass("selected");
        $(contents).removeClass("selected").hide();

        var tab_content = $(tab).attr("href") || $(tab).children().attr("href");
        $("*[href=" + tab_content + "]").parent().addClass("selected");
        $(tab_content).addClass("selected").show();
    };
    $(tabs).click(function () {
        instance.to(this);
        return false; // in order not to follow the link
    });
    // first shown tab is the first matched element in DOM tree
    this.to($(tabs)[0]);
}

/*
 * retrieve params from url
 */
function getUrlVars(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
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
                jQuery(this).val('');/*this.value = '';*/
            }
            else if(type == 'hidden' && this.name !== "csrfmiddlewaretoken"){
                jQuery(this).val('');/*this.value = '';*/
            }
            else if (type == 'checkbox' || type == 'radio'){
                jQuery(this).attr('checked', false);/*this.checked = false;*/
            }
            else if (tag == 'select'){
                jQuery(this).val('');/*this.selectedIndex = -1;*/
            }
        });
    };
})(jQuery);

/*
 * Extensao do jquery para tratar um form via ajax.
 * em caso de sucesso limpa o form e chama um callback
 * em caso de falha "pendura" os erros, usando o validate-box do easy-UI
 * uso:
 *   jQuery('#meu_form').ajaxform(function(retorno){
 *       // sua funcao de callback aqui
 *       // ...
 *   });
 *
 */
(function($){
    $.fn.ajaxform = function(config) {
        var $form =  this;

        /*  callback configs  */
        if (config && config.onSubmit){
            $form.onSubmit = config.onSubmit;
        }
        if (config && config.onSuccess){
            $form.onSuccess = config.onSuccess;
        }
        if (config && config.onError){
            $form.onError = config.onError;
        }
        if (config && config.onFocus){
            $form.onFocus = config.onFocus;
        }

        $form.submit( function(evt){
            evt.preventDefault();
            if ($form.onSubmit) {
                $form.onSubmit();
            }
            $.post(
                $form.attr('action'),  /* url */
                $form.serialize(),        /* dados */
                function(data){           /* callback */
                    if (data){
                        var validation_div;
                        /* em caso de sucesso limpa forma e chama callback */
                        if (data.success === "true"){
                            $form.clearForm();
                            validation_div = $('#validation-error');
                            if(validation_div.length){
                                validation_div.remove();
                            }
                            if ($form.onSuccess){
                                $form.onSuccess(data);
                            }
                        /* em caso de erro, trata os erros */
                        } else if (data.success === "false") {
                            var message = '<br/>';
                            $.each(data.errors, function(key,val){
                                if( key === "__all__"){
                                    message += '<span class="error-field" style="color: #cc2222;">Erro</span> &nbsp; - &nbsp; '+ val + '<br/>';
                                }else{
                                    message += '<span class="error-field" style="color: #cc2222;">' + key + '</span> &nbsp; - &nbsp; '+ val + '<br/>';
                                }
                            });
                            message += '<br/>';
                            validation_div = $('#validation-error');
                            if (validation_div.length){
                                validation_div.remove();
                            }
                            $form.append('' +
                                '<div id="validation-error" class="alert-message block-message error fade in" data-alert="alert" >' +
                                '<a class="btnClose" style="float:right;color:#000000;font-size:20px;font-weight:bold;' +
                                'line-height:13.5px;text-shadow:0 1px 0 #ffffff;filter:alpha(opacity=25);'+
                                '-khtml-opacity:0.25;-moz-opacity:0.25;opacity:0.25;"' +
                                'href="#">&times;</a>'+ message + '</div>');
                            $('.btnClose').live('click', function(e){
                                e.preventDefault();
                                $('#validation-error').alert('close');

                            });
                            if ($form.onError){
                                $form.onError(data);
                            }
                        }
                    }
                }
            );
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
        var $selectedChildren = $children; // starts manipulating all subitems

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
                width: 745,
                modal: true,
                resizable: false,
                draggable: false,
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
                class: "button",
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
