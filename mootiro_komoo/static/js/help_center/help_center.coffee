$ = jQuery


class HelpCenter
    constructor: (btn_selector, questions_ids, tour_id) ->
        @button = $(btn_selector)
        @button.on 'click', @show
        @questions = (@questions_config[cid] for cid in questions_ids)
        @tour = @tours_config[tour_id] if tour_id
        @modal_setup()
        @tour_setup()

    # TODO: put these html templates into an html file
    tour_tpl:
        "
        <!------------ PAGE TOUR ----------->
        <ol id='joyride'>
          <% for (var j = 0; j < tour.slides.length; j++) { %>
          <li data-id='<%= tour.slides[j].target_id %>' data-button='Next' data-options='<%= tour.slides[j].options %>'>
            <h2><%= tour.slides[j].title %></h2>
            <p><%= tour.slides[j].body %></p>
          </li>
          <% } %>
        </ol>
        <!--------------------------------->
        "

    modal_tpl:
        "
        <div id='help_center' class='modal hide fade'>
          <div class='modal-header'>
            <button type='button' class='close' data-dismiss='modal'>×</button>
            <h2>Central de Ajuda</h2>
          </div>
          <section class='modal-body'>
            <ul id='questions'>
              <% for (var i = 0; i < questions.length; i++) { %>
              <li class='<%= questions[i].type %>'>
                <!------------ QUESTION ----------->
                <article>
                  <h3><%= questions[i].title %></h3>
                  <p><%= questions[i].body %></p>
                </article>
                <!--------------------------------->
              </li>
              <% } %>
            </ul>

            <button id='tour_button'>Faça o tour desta página</button>
          </section>
        </div>
        "

    modal_setup: =>
        html = _.template @modal_tpl, {questions: @questions}
        @$modal = $(html)
        @$modal.modal {show: true}
        $('body').append @$modal

    tour_setup: =>
        html = _.template @tour_tpl, {tour: @tour}
        @$tour_content = $(html)
        $('body').append @$tour_content

        modal_wrap = @$modal

        $('button#tour_button', @$modal).on 'click', () ->
            modal_wrap.modal 'hide'
            $('#joyride').joyride {}

    show: () =>
        @$modal.modal('show')

    # TODO:use requires and put this json into other file
    questions_config:
        "organization:what_is":
            "title": "What is an organization?"
            "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu quam odio, ac sagittis nisi. Nam et scelerisque ligula. Ut id velit eu nulla interdum aliquam luctus sed odio. Suspendisse et nunc at ipsum sodales euismod. Vivamus scelerisque rutrum leo id blandit. Maecenas vel risus magna, at pulvinar turpis."

    tours_config:
        "maps:initial_tour":
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

        "organization:page_tour":
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
