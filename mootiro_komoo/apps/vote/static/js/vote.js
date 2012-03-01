(function($){

  var vote = (function(){
    $vote_links = $('.vote a');

    var init = function(){

      $vote_links.live('click', function(evt){
        /* click on any vote link */
        evt.preventDefault();
        var _this = $(evt.target),
            div_vote = _this.parent().parent();

        /* gather arguments info for the ajax request */
        args = {};
        args.vote = _this.parent().is('.vote-up') ? 'up' : 'down';
        args.csrfmiddlewaretoken = csrftoken;
        args.content_type = div_vote.attr('content-type');
        args.object_id = div_vote.attr('object-id');

        /* ajax post on /vote/add/  */
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
            /* holy crap, we have an error =( */
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
