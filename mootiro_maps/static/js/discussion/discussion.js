(function() {
  var $;

  $ = jQuery;

  $(function() {
    var $discussion, hash;
    $discussion = $("#content-discussion").detach();
    $discussion.insertAfter($content);
    $("#view-content-info").on('click', function(evt) {
      $content.show();
      return $discussion.hide();
    });
    $("#view-discussion-info").on('click', function(evt) {
      $discussion.show();
      return $content.hide();
    });
    hash = window.location.hash;
    if (hash === "#discussion") {
      return $("#view-discussion-info").click();
    } else {
      return $("#view-content-info").click();
    }
  });

}).call(this);
