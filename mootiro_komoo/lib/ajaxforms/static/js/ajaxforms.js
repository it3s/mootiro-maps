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

        $form.submit(function(evt){
            evt.preventDefault();
            if ($form.onSubmit) {
                $form.onSubmit();
            }

            $.post(
                $form.attr('action'),  /* url */
                $form.serialize(),        /* dados */
                function(data){           /* callback */
                    console.dir(data);
                    if (data){
                        var validation_div;
                        /* em caso de sucesso limpa forma e chama callback */
                        if (data.success === "true"){
                            // clean form
                            $form.clearForm();
                            // clean error messages
                            $('#validation-error').remove();
                            $('div.alert-message.error').remove();
                            $('.control-group.error').removeClass('error');


                            if ($form.onSuccess){
                                $form.onSuccess(data);
                            }
                            if (data.redirect){
                                window.location = data.redirect;
                            }
                        /* em caso de erro, trata os erros */
                        } else if (data.success === "false") {
                            // clean error messages
                            $('#validation-error').remove();
                            $('div.alert-message.error').remove();
                            $('.control-group.error').removeClass('error');

                            $.each(data.errors, function(key,val){
                                console.log(key)
                                if( key === "__all__"){
                                    message = '<span class="error-field" style="color: #cc2222;">Erro</span> &nbsp; - &nbsp; '+ val + '<br/>';
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
                                }

                                // new validation style
                                var node = $('#id_' + key);
                                console.log('#id_' + key);
                                for (i=0; ! node.is('.controls') && i < 5; node = node.parent(), i++);
                                // node.append('<span class="inline-help">'+ val + '</span>')
                                node.append('' +
                                '<div class="alert-message block-message error fade in" data-alert="alert" >' +
                                '<a class="btnClose" style="float:right;color:#000000;font-size:20px;font-weight:bold;' +
                                'line-height:13.5px;text-shadow:0 1px 0 #ffffff;filter:alpha(opacity=25);'+
                                '-khtml-opacity:0.25;-moz-opacity:0.25;opacity:0.25;"' +
                                'href="#">&times;</a>'+ val + '</div>')
                                node.parent().addClass('error');
                            });

                            $('.btnClose').live('click', function(e){
                                e.preventDefault();
                                $(this).parent().slideUp();

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
