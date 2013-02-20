$ = jQuery


class HelpCenter
    constructor: (btn_selector, content_ids) ->
        @button = $(btn_selector)
        @button.on 'click', @show
        @contents = (@contents_config[cid] for cid in content_ids)
        @modal_setup()

    question_tpl:
        "
        <article>
            <h3><%= question %></h3>
            <p><%= answer %></p>
        </article>
        "

    tutorial_tpl:
        "
        tourtorial
        "

    # TODO: put this into an html file
    modal_tpl:
        "
        <div id='help_center' class='modal hide fade'>
          <div class='modal-header'>
            <button type='button' class='close' data-dismiss='modal'>×</button>
            <h2>Modal header</h2>
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
                  <article>
                    <h3><%= contents[i].title %></h3>
                    <p><%= contents[i].body %></p>
                  </article>
                  <ol id='joyride'>
                    <% for (var j = 0; j < contents[i].slides.length; j++) { %>
                    <li data-id='<%= contents[i].slides[j].target_id %>' data-button='Next' data-options='<%= contents[i].slides[j].options %>'>
                      <h2><%= contents[i].slides[j].title %></h2>
                      <p><%= contents[i].slides[j].body %></p>
                    </li>
                    <% } %>
                  </ol>
                <!--!------------------------------>
                <% } %>
              </li>
              <% } %>
            </ul>
          </section>
        </div>

        "

    modal_setup: =>
        html = _.template @modal_tpl, {contents: @contents}
        @$modal = $(html)
        modal_wrap = @$modal
        $('li.tutorial', @$modal).on 'click', () ->
            li = $(this)
            # modal_wrap.modal 'hide'
            console.log $('#joyride', li)
            $('#joyride', li).joyride {}
            console.log 'STARTOUR'

        @$modal.modal {show: true}
        $('body').append @$modal

    show: () =>
        @$modal.modal('show')

    # TODO:use requires and put this json into other file
    contents_config:

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
                "title": "Description"
                "body": "This is the organization description"
                "target_id": "#logo"
                "options": "tipLocation:top;tipAnimation:fade"
                },
                {
                "title": "Contact information"
                "body": "Here you'll find contact"
                "target_id": ".view-list-visualization-header"
                "options": ""
                }
            ]


window.HelpCenter = HelpCenter
