(function($){
    comments = (function(){

        var $formComment = $('#formComment');
        var $btnSubCommentAdd = $('.btnSubCommentAdd');
        var $btnShowForm = $('.btnShowForm');
        var $link_subcomments = $('.link_subcomments');

        var init = function(){

            $btnShowForm.click(function(evt){
                $formComment.slideToggle('fast');
            });

            // add sub-comment
            $btnSubCommentAdd.live('click', function(evt){
                evt.preventDefault();
                btnSubCommentAdd(evt.target);
            });

            $link_subcomments.click(function(evt){
                evt.preventDefault();
                var link = $(evt.target);

                var div_comment_list = link.parent().parent().find('.comments-list');
                if (div_comment_list.length){
                    div_comment_list.slideToggle('fast');
                } else {
                    $.get('/comments/load', {id:link.attr('comment-id')}, function(data){
                        var i, comment, csrftoken, subcomments_list;
                        csrftoken = $formComment.find('input[name=csrfmiddlewaretoken]').val();

                        if (data.success){
                            subcomments_list = '<div class="comments-list" style="display: none;">'

                            for (i in data.comments){
                                comment = data.comments[i];
                                subcomments_list += '' +
                                    '<div class="comment-container inner-comment" commentID="' + comment.id + '">' +
                                        '<div class="comment-header">' +
                                            '<a href="#">' + comment.author + '</a>' + comment.pub_date  +
                                            ((comments.sub_comments > 0) ? ('(' + comment.sub_comments + ' respostas)') : '') +
                                            '<a href="#">Denunciar</a>'+
                                        '</div>'+
                                        '<div class="comment" >' +
                                            comment.content +
                                        '</div>' +
                                        '<div class="comment-footer">' +
                                            '<a class="btnSubCommentAdd" href="#">Responder</a>' +
                                            ((comment.sub_comments > 0 ) ? (
                                                '<a class="link_subcomments" href="" comment-id="' + comment.id + '">' +  comment.sub_comments + 'resposta(s)</a>') : '') +
                                            "<div class='comment-form'>" +
                                                "<form method='post' class='stacked-form' action='/comments/add/' >" +
                                                    '<fieldset>' +
                                                        "<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrftoken + "' /></div>" +
                                                        "<label>Comment:</label><textarea rows='5' cols='80' name='comment' class='span8'></textarea>" +
                                                        "<input type='hidden' name='parent_id' value='" + comment.id + "' />" +
                                                        "<div class='clearfix'>" +
                                                            "<input type='submit' class='button' value='save'/>" +
                                                        '</div>' +
                                                    '</fieldset>' +
                                                '</form>' +
                                            '</div>' +
                                        '</div>' +
                                    '</div>'
                            }

                            subcomments_list += '</div>'
                            link.parent().parent().append(subcomments_list).find('.comments-list').slideToggle('fast');
                        }
                    });
                }
            });

        }

        var btnSubCommentAdd = function(btn){
            $(btn).parent().find('.comment-form').slideToggle('fast');
        };

        return { init : init }
    })();

    $(function(){
        comments.init()

    });

})(jQuery)
