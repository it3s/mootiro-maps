/*
* imageTick for jQuery
* http://boedesign.com/blog/2008/06/08/imagetick-for-jquery/
*
* Copyright (c) 2011 Jordan Boesch
* Dual licensed under the MIT and GPL licenses.
*
* Date: February 5, 2011
* Version: 2.2
* 
* Modified by André Casimiro
* Date: April 4, 2012
* Lines: 183-187
*/

(function($){
	
    // Global setters
    $.imageTick = {
        logging: false
    };
    
    /*
    * Init the imageTick function.  We can do 1 of 2 things with this.  We can
    * either initialize it and turn those nasty checkboxes/radios into something
    * awesome... or we can put disabled attributes on certain elements
    *
    * @param options {Object/String} An object of options to pass in, this can be a string of "disabled" as well
    * @param disable {Boolean} If we did pass a 'disabled' string as a first param, we need to say whether we're disabling or enabling (true/false)
    */
    $.fn.imageTick = function(options, disable) {

        var defaults = {	
            tick_image_path: "",
            no_tick_image_path: "",
            image_tick_class: "ticks_" + Math.floor(Math.random() * 999999),
            img_html: '<img src="%s1" alt="no_tick" class="%s2" id="tick_img_%s3" />',
            custom_button: false,
            custom_button_selected_class: 'selected'
        };
        	
        var opt = $.extend({}, defaults, options);
        
        // Private options
        opt._tick_img_id_format = 'tick_img_%s';
        opt._valid_types = ['checkbox', 'radio'];
        
        // Quick logging
        function log(){
            $.imageTick.logging && console && console.log && console.log.apply(console, arguments);
        }
        
        // If we aren't initializing anything, we're just disabling and re-enabling 
        // certain input checkboxes/radios
        if(options === 'disabled'){
            
            if(this.selector.indexOf('#') == -1){
                log('COULD NOT DISABLE "' + this.selector + '": You need to specify the id of the <input> when calling disabled true/false.');
                return;
            }
            
            var $img_id = $('#' + opt._tick_img_id_format.replace('%s', this[0].id));
            
            if(disable){
                $(this).attr('disabled', 'disabled');
                method_type = 'add';
            }
            else {
                $(this).removeAttr('disabled');
                method_type = 'remove';
            }
            
            $img_id[method_type + 'Class']('disabled');
            return;
             
        }
		
        /*
        * When we click on the image, we need to compare images to see if we're
        * on a checked state or a non-checked state, IE needs this cause it handles
        * image paths as absolute urls. Here we just strip off the file name and use that.
        *
        * @param e {DOMElement} The DOM element of the image we just clicked on
        */
        function imagePathsAreEqual(e){
            
            var current_img_src = e.src.split('/').pop();
            var no_tick_path = opt.no_tick_image_path.split('/').pop();
        	
            return current_img_src == no_tick_path;
            
        }
		
        /*
        * When the user clicks on the radio/checkbox image, they are taken to this function to
        * determine what to do with the cooresponding labels and inputs. If we're using a custom
        * button, we need to do things a little differently here.
        *
        * @param using_custom_button {Boolean} Are we using a custom button or default image
        * @param type {String} Is it a 'checkbox' or a 'radio'
        * @param $input_id {jQuery Object} The id of the real <input>
        */
        function handleClickType(using_custom_button, type, $input_id){
            
            if(using_custom_button){
                
                if(type == 'radio'){
                    $("." + opt.image_tick_class).removeClass(opt.custom_button_selected_class);
                }
                $(this).toggleClass(opt.custom_button_selected_class);
                
            }
            else {
                
                if(type == 'checkbox'){
                    var img_src = (imagePathsAreEqual(this)) ? opt.tick_image_path : opt.no_tick_image_path;
                }
                else {
                    $("." + opt.image_tick_class).attr('src', opt.no_tick_image_path);
                    var img_src = opt.tick_image_path;
                }

                this.src = img_src;
                
            }
		  
        }
		
        // Loop through each one of our elements
        return this.each(function(){
			
            var $obj = $(this);
            var type = $obj[0].type; // radio or checkbox
			
            if($.inArray(type, opt._valid_types) == -1){
                throw new Error(type + ' is not a valid input type. Must be radio or checkbox.');
            }
			
            var id = $obj[0].id;
            var $input_id = $('#' + id);
            var $label = $("label[for='" + id + "']");
            var img_id_format = opt._tick_img_id_format.replace('%s', id);
            var using_custom_btn = $.isFunction(opt.custom_button);
            var img_html = '';
            
            // Custom button
            if(using_custom_btn){
                img_html = $(opt.custom_button($label)).attr('id', img_id_format.replace('%s', id)).addClass(opt.image_tick_class);
            }
            else {
                img_html = opt.img_html.replace('%s1', opt.no_tick_image_path).replace('%s2', opt.image_tick_class).replace('%s3', id);
            }
			
            $obj.before(img_html).hide();
            var $img_id = $('#' + img_id_format);
            
            // Give any disabled inputs a disabled class on the img/custom button
            if($input_id[0].disabled){
                $img_id.addClass('disabled');
            }
			
            // If something has a checked state when the page was loaded
            if($obj[0].checked){
                // Make sure it's an image we're dealing with
                if($img_id[0].src){
                    $img_id[0].src = opt.tick_image_path;
                }
                // Dealing with custom buttons
                else {
                    $img_id.addClass(opt.custom_button_selected_class);
                }
            }
            
            // Delegate the click off to a function that will determine what to do with
            // it based on if it's a checkbox or a radio button
            $img_id.click(function(e){
                // Check each time we click on an element, it might change!
                if($input_id[0].disabled){
                    return;
                }
                e.preventDefault();

                $input_id.trigger("click");
                // Apparently it is not enough to trigger click() for a
                // checkbox to change its state. - André Casimiro
                // if (type == "checkbox") {
                //     alert($input_id.attr('checked'));
                //     var val = ($input_id.attr('checked') == undefined) ? false : true;
                //     $input_id.attr('checked', !$input_id.attr('checked'));
                // }
                
                handleClickType.call(this, using_custom_btn, type, $input_id);
            });
			
            // Handle clicks for the labels
            if($label.length){
                $label.click(function(e){
                    e.preventDefault();	
                    $img_id.trigger('click');
                });
            }
			
        });
    };
	
})(jQuery);
