$ = jQuery

class HelpCenter
    constructor: (btn_selector, @content_ids) ->
        @button = $(btn_selector)
        @button.on 'click', @show
        @modal_setup()

    modal_setup: =>
        html = "
            <div id='help_center' class='modal hide fade'>
                <div class='modal-header'>
                    <button type='button' class='close' data-dismiss='modal'>×</button>
                    <h3>Modal header</h3>
                </div>
                <div class='modal-body'>
                    <p>One fine body…</p>
                </div>
            </div>
        "
        @$modal = $(html).modal {show: false}
        $('body').append @$modal

    show: () =>
        console.log @content_ids
        console.log @contents
        @$modal.modal('show')

    # TODO:use requires and put this json into other file
    contents:
        "organization:what_is":
            "type": "question"
            "data":
                "question": "What is an organization?"
                "answer": "An organization is ... (markdown string)"

        "organization:page_tour":
            "type": "tour"
            "data":
                "slides": [
                    {
                    "title": "Description"
                    "body": "This is the organization description"
                    "target": "#organization-description"
                    },
                    {
                    "title": "Contact information"
                    "body": "Here you'll find contact"
                    "target": "#organization-contact"
                    }
                ]


window.HelpCenter = HelpCenter
