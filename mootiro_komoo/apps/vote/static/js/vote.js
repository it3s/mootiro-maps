(function($){

    var vote = (function(){
        $vote = $('.vote');
        $vote_up = $('.vote-up');
        $vote_down = $('.vote-down');

        var init = function(){

        };

        return { init : init };
    })();

    $(function(){
        vote.init();
    });
})(jQuery);
