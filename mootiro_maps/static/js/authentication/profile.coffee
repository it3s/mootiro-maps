$ = jQuery

window.Contribution = Backbone.Model.extend
    imageName: () ->
        "/static/img/updates-page/#{@model_name}-#{@typeExt()}.png"

    typeExt: (translated=false)->
        _type = {
            A: 'added'
            E: 'edited'
            C: 'discussed'
            D: 'deleted'
        }[@type]
        if translated then gettext _type else _type

    modelPrettyName: () ->
        namesMapper =
            organization: gettext 'Organization'
            need: gettext 'Need'
            community: gettext 'Community'
            resource: gettext 'Resource'
        namesMapper[@model_name]

    actionDesc: () ->
        at_trans = gettext 'at'
        "#{@modelPrettyName()} #{@typeExt(true)} #{at_trans} #{@date}."

    toJSON: (attr) ->
        defaultJSON = Backbone.Model.prototype.toJSON.call this, attr
        _.extend defaultJSON, {
            imageName: @imageName
            actionDesc: @actionDesc
            typeExt: @typeExt
            modelPrettyName: @modelPrettyName
        }


window.Contributions = Backbone.Collection.extend
    model: Contribution


window.ContributionView = Backbone.View.extend
    tagName: 'div'
    className: 'contribution'
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $('#contribution-template').html()

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


