(function($){

    comments = (function(){

        var $btnFormCommentSubmit = $('#btnFormCommentSubmit');
        var $formComment = $('#formComment');
        var $btnSubCommentAdd = $('.btnSubCommentAdd');
        var $linkSubComments = $('.linkSubComments');
        var $btnShowForm = $('.btnShowForm');
        var $csrftoken = $formComment.find('input[name=csrfmiddlewaretoken]')

        var init = function(){

            $btnShowForm.click(function(evt){
                $formComment.slideToggle('fast');
            });

            $btnFormCommentSubmit.click(function(evt){
                evt.preventDefault();
                addComment();
            });

            // add sub-comment
            $btnSubCommentAdd.live('click', function(evt){
                evt.preventDefault();
                btnSubCommentAdd(evt.target);
            });

            // $linkSubComments.click(function(evt){
            //     evt.preventDefault();
            //     var comment_id = $(this).parent().parent().children().first().attr('commentID')
            //     console.log(comment_id);
            // });
        }

        var btnSubCommentAdd = function(btn){
            $(btn).parent().find('.comment-form').slideToggle('fast');

        };

        var addComment = function(){
            $.post('/comments/add/', $formComment.serialize(), function(data) {
                if (data.success){
                    //here we want to explicitly re-do this query
                    $('#comments-list').prepend("" + 
                        "<div class='comment-container' commentID='" + data.comment.id + "'>" + 
                            "<div class='comment'>" + 
                                data.comment.comment + " - [" + data.comment.pub_date + "]" +
                            "</div>" + 
                            "<div class='comment-add'>" + 
                                "<a class='btnSubCommentAdd' href='#'>Responder</a>" + 
                            "</div>" + 
                        "</div>"
                    );
                    $formComment.clearForm();
                } else {
                    alert('error saving comment: ' + data.errors);
                }
            } , 'json');
        }

        return {
            init : init, addComment : addComment
        } 
    })();

    $(function(){
        
        comments.init()

        
    });

})(jQuery)