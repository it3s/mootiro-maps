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
                        <li>
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
                            <div id='tutorial' class='tutorial'>
                                <% for (var j = 0; j < contents[i].slides.length; j++) { %>
                                <div
                                  data-target='<%= contents[i].slides[j].target %>'
                                  data-location='<%= contents[i].slides[j].location %>'
                                  data-arrow='<%= contents[i].slides[j].arrow %>'
                                >
                                    <h3><%= contents[i].slides[j].title %></h3>
                                    <p><%= contents[i].slides[j].body %></p>
                                </div>
                                <% } %>
                            </div>
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
        console.log "@contents", @contents
        @$modal = $(html).modal {show: true}
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
                "target": "#organization-description"
                "location": "tl"
                "arrow": "tc"
                },
                {
                "title": "Contact information"
                "body": "Here you'll find contact"
                "target": "#organization-contact"
                "location": "tl"
                "arrow": "tc"
                }
            ]


window.HelpCenter = HelpCenter
