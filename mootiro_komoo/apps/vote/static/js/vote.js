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
            if (! data.create) {
              // remove active state from older vote and reduces its count
              var div_vote = _this.parent().parent();
              var old_vote = div_vote.find('.active').removeClass('active');
              var old_vote_num = old_vote.find('.vote-num:first');
              old_vote_num.text(parseInt(old_vote_num.text(), 10) - 1);
            }
            // add active class to new vote and increases its count
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
