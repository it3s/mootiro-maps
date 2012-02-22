(function($){
    comments = (function(){
        var $btnShowForm = $('.btnShowForm');
        var $link_subcomments = $('.link_subcomments');
        var $btnFormCommentSubmit = $('.btnFormCommentSubmit');
        var csrftoken = $('#formComment').find('input[name=csrfmiddlewaretoken]').val();

        var init = function(){

            // comment form toggle
            $btnShowForm.live('click', function(evt){
                evt.preventDefault();
                $(evt.target).siblings('.link_subcomments').click();
                $(evt.target).siblings('.comment-form').slideToggle('fast');
                return false;
            });

            // add subcomments list
            $link_subcomments.live('click', function(evt){
                evt.preventDefault();
                var link = $(evt.target);

                var div_comment_list = link.parent().parent().find('.comments-list:first');
                if (div_comment_list.length){
                    div_comment_list.slideToggle('fast');
                } else {
                    $.get('/comments/load', {parent_id:link.attr('comment-id')}, function(data){
                        console.log(data.comments);
                        var link_parent = link.parent().parent();
                        link_parent.append(data.comments).find('.comments-list').slideToggle('fast');
                    });
                }
            });

            $btnFormCommentSubmit.live('click', function(evt){
                var form, tmp;
                evt.preventDefault();

                for(tmp = $(evt.target); !tmp.is('form'); tmp = tmp.parent());
                form = tmp;

                $.post(form.attr('action'), form.serialize(), function(data){
                    var div_;
                    if (data.success){
                        div_ = form.parent().siblings('.comments-list');
                        div_.prepend(data.comment);

                        form.parent().slideToggle('fast');
                        form.clearForm();
                    }
                }, 'json');
            });

        };

        return { init : init };
    })();

    $(function(){
        comments.init();

    });

})(jQuery);
