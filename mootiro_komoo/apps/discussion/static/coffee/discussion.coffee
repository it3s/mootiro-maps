$ = jQuery

$ () ->
    # Initial discussion insertion to after DOM content
    $discussion = $("#content-discussion").detach()
    $discussion.insertAfter $content

    $("#view-content-info").on 'click', (evt) ->
        $content.show()
        $discussion.hide()

    $("#view-discussion-info").on 'click', (evt) ->
        $discussion.show()
        $content.hide()

    hash = window.location.hash
    if hash == "#discussion"
        $("#view-discussion-info").click();
    else
        $("#view-content-info").click();
