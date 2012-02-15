/*
 * A jQuery plugin for clearing forms
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