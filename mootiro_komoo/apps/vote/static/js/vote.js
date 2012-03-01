(function($){

    var vote = (function(){
        $vote = $('.vote');
        $vote_up = $('.vote-up');
        $vote_down = $('.vote-down');
        $vote_links = $vote.find('a');

        var init = function(){
            $vote_links.live('click', function(evt){
                evt.preventDefault();
                var _this = $(evt.target),
                    div_vote = _this.parent().parent();

                args = {};
                args.vote = _this.parent().is('.vote-up') ? 'up' : 'down';
                args.csrfmiddlewaretoken = csrftoken;
                args.content_type = div_vote.attr('content-type');
                args.object_id = div_vote.attr('object-id');

                $.post(_this.attr('href'), args, function(data){
                    if (data.success){
                        _this.parent().addClass('active');
                        var vote_num = _this.siblings('.vote-num:first');
                        vote_num.text(parseInt(vote_num.text(),10) + 1);
                    } else {
                        alert('falha : ' + data.error);
                    }
                }, 'json');
            });
        };

        return { init : init };
    })();

    $(function(){
        vote.init();
    });
})(jQuery);
