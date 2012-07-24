$ = jQuery

window.Contribution = Backbone.Model.extend
    bla: () ->
        console.log 'blaa'

window.Contributions = Backbone.Collection.extend
    model: Contribution

window.ContributionView = Backbone.View.extend
    tagName: 'li'
    className: 'contribution'
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $('#contribution-template').html()

    render: () ->
        renderedContent = @template @model.toJSON()
        $(@el).html renderedContent
        this

window.ContributionsView = Backbone.View.extend {}


