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

        $form.data('is_ajaxform', true);

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
                    if (data){
                        var validation_div;
                        /* em caso de sucesso limpa forma e chama callback */
                        if (data.success === "true"){
                            // clean form
                            $form.clearForm();
                            // clean error messages
                            $('.error-field').remove();
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
                            $('.error-field').remove();
                            $('.control-group.error').removeClass('error');

                            $.each(data.errors, function(key,val){
                                if( key === "__all__"){
                                    validation_div = $('#validation-error');
                                    if (validation_div.length){
                                        validation_div.remove();
                                    }
                                    $form.append('' +
                                        '<div id="validation-error" class="error-field">' +
                                            '<img src="/static/img/erro.png" />'+
                                            '<span class="error-notice">Erro:</span>' +
                                            val +
                                        '</div>');
                                }

                                // new validation style
                                var node = $form.find('#id_' + key);
                                if (! node.length) {
                                    node = $form.find('input[name=' + key + ']');
                                }
                                for (i=0; ! node.is('.controls') && i < 5; node = node.parent(), i++);
                                node.append('' +
                                '<div class="error-field">' +
                                    '<img src="/static/img/erro.png" />'+
                                    '<span class="error-notice">Erro:</span>' +
                                    val +
                                '</div>');
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
