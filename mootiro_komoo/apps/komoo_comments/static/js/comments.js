(function($){
    comments = (function(){
        var $btnShowForm = $('.btnShowForm');
        var $link_subcomments = $('.link_subcomments');
        var $btnFormCommentSubmit = $('.btnFormCommentSubmit');
        var csrftoken = $('#formComment').find('input[name=csrfmiddlewaretoken]').val();

        var init = function(){

            // $('.comment-form').hide();

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
                    $.get('/comments/load', {id:link.attr('comment-id')}, function(data){
                        var i, comment, subcomments_list, link_parent;
                        link_parent = link.parent().parent();
                        if (data.success){
                            subcomments_list = '<div class="comments-list inner-list">'

                            for (i in data.comments){
                                comment = data.comments[i];
                                subcomments_list += buildCommentMarkup(comment, (link_parent.hasClass('odd')? 'inner-comment' : 'inner-comment odd'));
                            }

                            subcomments_list += '</div>'
                            link_parent.append(subcomments_list).find('.comments-list').slideToggle('fast');
                        }
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
                        if(form.is('#formComment')){
                            div_ = form.parent();
                        } else {
                            for(; !tmp.is('.comment-footer'); tmp = tmp.parent());
                            div_ = tmp
                        }

                        if (!div_.siblings('.comments-list').length){
                            div_.after('<div class="comments-list inner-list" ></div>');
                            console.log('creating div comments-list');
                        }
                        div_.siblings('.comments-list').prepend(buildCommentMarkup(data.comment, ''));

                        form.parent().slideToggle('fast');
                        form.clearForm();
                    }
                }, 'json');
            });

        }

        var buildCommentMarkup = function(comment, class_){
            return ('<div class="comment-container ' + class_ + '" commentID="' + comment.id + '">' +
                        '<div class="comment-header">' +
                            '<a href="#">' + comment.author + '</a>' + comment.pub_date  +
                            ((comment.sub_comments > 0) ? ('(' + comment.sub_comments + ' respostas)') : '') +
                            '<a href="#">Denunciar</a>'+
                        '</div>'+
                        '<div class="comment" >' +
                            comment.comment +
                        '</div>' +
                        '<div class="comment-footer">' +
                            '<a class="btnShowForm" href="#">Responder</a>' +
                            ((comment.sub_comments > 0 ) ? (
                                '<a class="link_subcomments" href="#" comment-id="' + comment.id + '">' +  comment.sub_comments + 'resposta(s)</a>') : '') +
                            "<div class='comment-form'>" +
                                "<form method='post' class='stacked-form' action='/comments/add/' >" +
                                    '<fieldset>' +
                                        "<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /></div>" +
                                        "<label>Comment:</label><textarea rows='5' cols='80' name='comment' class='span8'></textarea>" +
                                        "<input type='hidden' name='parent_id' value='" + comment.id + "' />" +
                                        "<div class='clearfix'>" +
                                            "<input type='submit' class='btnFormCommentSubmit button' value='save'/>" +
                                        '</div>' +
                                    '</fieldset>' +
                                '</form>' +
                            '</div>' +
                        '</div>' +
                    '</div>'
            );
        };

        return { init : init }
    })();

    $(function(){
        comments.init()

    });

})(jQuery)
