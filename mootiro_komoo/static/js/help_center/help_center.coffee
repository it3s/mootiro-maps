$ = jQuery

class HelpCenter
    constructor: (btn_selector, @content_ids) ->
        alert 'constructor'
        @button = $(btn_selector)
        @button.on 'click', @show

    show: () =>
        console.log @content_ids

window.HelpCenter = HelpCenter
