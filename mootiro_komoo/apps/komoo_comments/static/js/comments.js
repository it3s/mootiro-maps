(function($){

    comments = (function(){

        var $btnFormCommentSubmit = $('#btnFormCommentSubmit');
        var $formComment = $('#formComment');
        var $btnSubCommentAdd = $('.btnSubCommentAdd');
        var $linkSubComments = $('.linkSubComments');
        var $csrftoken = $formComment.find('input[name=csrfmiddlewaretoken]')

        var init = function(){
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
            var parent = $(btn).parent();
            var comment_id = parent.parent().attr('commentID');
            var csrftoken = $csrftoken.val();
            $(btn).css('display', 'none');
            parent.append('' + 
                '<div class="comment-form">' + 
                    '<form method="post" action="/comments/add/">' + 
                        '<label>Comment: </label><input type="text" name="comment" />' + 
                        '<input type="text" name="parent_id" style="display: none;" value="' + comment_id + '" />' + 
                        '<input type="text" name="csrfmiddlewaretoken" style="display: none;" value="' + csrftoken + '" />' + //TODO csrftoken
                        '<input type="submit" class="button" value="save"/>' + 
                    '</form>' + 
                '</div>'
            );  
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