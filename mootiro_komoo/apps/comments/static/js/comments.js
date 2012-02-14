(function($){

    comments = (function(){

        var $btnFormCommentSubmit = $('#btnFormCommentSubmit');
        var $formComment = $('#formComment');
        var $btnCommentAdd = $('.btnCommentAdd');
        var $linkSubComments = $('.linkSubComments');

        var init = function(){
            $btnFormCommentSubmit.click(function(evt){
                evt.preventDefault();
                $.post('/comments/add/', $formComment.serialize(), function(data) {
                    console.log('json returned?');
                    $('#comments-list').append("" + 
                        "<div class='comment-container' style='margin-top:20px;'>" + 
                            "<div class='comment' commentID='" + data.comment.id + "'>" + 
                                data.comment.comment + " - [" + data.comment.pub_date + "]" +
                            "</div>" + 
                            "<div class='comment-add'>" + 
                                "<input type='button' class='btnCommentAdd' value='comment' />" + 
                            "</div>" + 
                        "</div>"
                    );
                } , 'json');
            });

            $btnCommentAdd.live('click', function(evt){
                evt.preventDefault();
                var parent = $(this).parent();
                var comment_id = parent.parent().children().first().attr('commentID')
                $(this).css('display', 'none');
                parent.append('' + 
                    '<div class="comment-form">' + 
                        '<form methos="POST" action="/comments/add/">' + 
                            '<label>Comment: </label><input type="text" name="comment" />' + 
                            '<input type="text" name="parent_id" style="display: none;" value="' + comment_id + '" />' + 
                            '<input type="submit" value="save"/>' + 
                        '</form>' + 
                    '</div>'
                );
            });

            $linkSubComments.click(function(evt){
                evt.preventDefault();
                var comment_id = $(this).parent().parent().children().first().attr('commentID')
                console.log(comment_id);
            });
            }

        return {
            init : init
        } 
    })();

    $(function(){
        
        comments.init()

        
    });

})(jQuery)