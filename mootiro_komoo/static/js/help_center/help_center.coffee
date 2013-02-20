$ = jQuery


class HelpCenter
    constructor: (btn_selector, content_ids) ->
        @button = $(btn_selector)
        @button.on 'click', @show
        @contents = (@contents_config[cid] for cid in content_ids)
        @modal_setup()
        @tutorials_setup()

    question_tpl:
        "
        <article>
            <h3><%= question %></h3>
            <p><%= answer %></p>
        </article>
        "

    # TODO: put these html templates into an html file
    tutorials_tpl:
        "
        <% for (var i = 0; i < contents.length; i++) { %>
          <!--!--------- TUTORIAL ----------->
          <% if (contents[i].type == 'tutorial') { %>
            <ol id='joyride<%= i %>' class=''>
              <% for (var j = 0; j < contents[i].slides.length; j++) { %>
              <li data-id='<%= contents[i].slides[j].target_id %>' data-button='Next' data-options='<%= contents[i].slides[j].options %>'>
                <h2><%= contents[i].slides[j].title %></h2>
                <p><%= contents[i].slides[j].body %></p>
              </li>
              <% } %>
            </ol>
          <% } %>
          <!--!------------------------------>
        <% } %>
        "

    modal_tpl:
        "
        <div id='help_center' class='modal hide fade'>
          <div class='modal-header'>
            <button type='button' class='close' data-dismiss='modal'>×</button>
            <h2>Help Center</h2>
          </div>
          <section class='modal-body'>
            <ul>
              <% for (var i = 0; i < contents.length; i++) { %>
              <li class='<%= contents[i].type %>'>

                <!--!--------- QUESTION ----------->
                <% if (contents[i].type == 'question') { %>
                <article>
                  <h3><%= contents[i].title %></h3>
                  <p><%= contents[i].body %></p>
                </article>
                <% } %>

                <!--!--------- TUTORIAL ----------->
                <% if (contents[i].type == 'tutorial') { %>
                  <article data-tutorial-id='<%= i %>'>
                    <h3><%= contents[i].title %></h3>
                    <p><%= contents[i].body %></p>
                  </article>
                <% } %>
                <!--!------------------------------>
              </li>
              <% } %>
            </ul>
          </section>
        </div>
        "

    modal_setup: =>
        html = _.template @modal_tpl, {contents: @contents}
        @$modal = $(html)
        @$modal.modal {show: false}
        $('body').append @$modal

    tutorials_setup: =>
        html = _.template @tutorials_tpl, {contents: @contents}
        @$tutorials = $(html)
        $('body').append @$tutorials

        modal_wrap = @$modal
        $('li.tutorial', @$modal).on 'click', () ->
            modal_wrap.modal 'hide'
            tutorial_id = $('article', this).attr('data-tutorial-id')
            console.log $('#joyride' + tutorial_id)
            $('#joyride' + tutorial_id).joyride {}

    show: () =>
        @$modal.modal('show')

    # TODO:use requires and put this json into other file
    contents_config:

        "maps:initial_tour":
            "type": "tutorial"
            "title": "Initial Tour"
            "body": "Take the tour."
            "slides": [
                {
                "title": "MootiroMaps"
                "body": "This is the logo."
                "target_id": "logo"
                "options": "tipLocation:bottom"
                },
                {
                "title": "End"
                "body": "Feel free... stay around..."
                "target_id": ""
                "options": ""
                }
            ]

        "organization:what_is":
            "type": "question"
            "title": "What is an organization?"
            "body": "An organization is ... (markdown string)"

        "organization:page_tour":
            "type": "tutorial"
            "title": "Organization page tour"
            "body": "Take the tour of this page"
            "slides": [
                {
                "title": "Welcome to the tour!"
                "body": "It's a pleasure to meet you."
                "target_id": ""
                "options": ""
                },
                {
                "title": "MootiroMaps"
                "body": "This is the MootiroMaps logo. You can click it anytime to get into website's homepage."
                "target_id": "logo"
                "options": "tipLocation:bottom"
                },
                {
                "title": "Map preview"
                "body": "Here is the organization in the map."
                "target_id": "map-container-preview"
                "options": "tipLocation:bottom"
                },
                {
                "title": "Footer"
                "body": "Can I <strong>bold this</strong>? <em>Yes</em>!"
                "target_id": "footer"
                "options": "tipLocation:top"
                },
                {
                "title": "End"
                "body": "Feel free... stay around..."
                "target_id": ""
                "options": ""
                },
            ]


window.HelpCenter = HelpCenter
