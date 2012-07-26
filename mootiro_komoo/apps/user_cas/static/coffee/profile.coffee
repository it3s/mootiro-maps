$ = jQuery

window.Contribution = Backbone.Model.extend {} 

window.Contributions = Backbone.Collection.extend
    model: Contribution


window.ContributionView = Backbone.View.extend
    tagName: 'div'
    className: 'contribution'
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $('#contribution-template').html()
        console.log 'Starting View for model', @model.toJSON()

    render: () ->
        renderedContent = @template @model.toJSON()
        $(@el).html renderedContent
        this

window.ContributionsView = Backbone.View.extend
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $("#contributions-template").html()
        @collection.bind 'reset', @render

    render: () ->
        $(@el).html @template({})
        $contributions = this.$ '.profile-cp-contributions'

        collection = @collection
        collection.each (contrib) ->
            view = new ContributionView
                model: contrib
                collection: collection
            $contributions.append view.render().el
        this


$ () ->
    loaded_contributions = new Contributions()
    loaded_contributions.reset window.KomooNS.contributions

    contributionsView = new ContributionsView
        collection: loaded_contributions

    $('.profile-central-pane').append contributionsView.render().el


