define [
    'jquery',
    'underscore',
    'backbone',
    'project/model',
    'widgets/autocomplete',
    'text!templates/project/_add_dialog.html',
    'bootstrap'
], ($, _, Backbone, Model, AutocompleteView, tplt) ->
    'use strict'

    ProjectAutocompleteView = AutocompleteView.extend
        inputName: 'project'
        autocompleteSource: '/project/search_by_name'
        className: 'project_autocomplete'

    AddDialogView = Backbone.View.extend
        events:
            'click .save':   'onSaveBtnClick'
            'click .cancel': 'onCancelBtnClick'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template tplt

            @autocomplete = new ProjectAutocompleteView().render()
            @autocomplete.$input.on 'autocompleteselect', (event, ui) =>
                @onProjectSelected ui.item

        open: () ->
            $('body').append @$el
            @$('.dialog').modal 'show'
            this

        close: () ->
            @$('.dialog').modal 'hide'
            this

        clear: () ->
            @autocomplete.clear()
            @$('.msg').html ''
            @$('.save').addClass 'disabled'
            this

        onCancelBtnClick: () ->
            @close()
            false

        onSaveBtnClick: () ->
            if @$('.save').hasClass 'disabled'
                false

            projectId = @autocomplete.val()
            if projectId
                project = new Model.Project id: projectId
                project.fetch()
                project.addObject(@model).done((project) =>
                    @trigger 'saved', project
                ).fail((project, msg) =>
                    @trigger 'failed', project, msg
                )
            false

        onProjectSelected: (item) ->
            @$('.msg').html "<p>Este objeto será adicionado ao projeto <strong> #{item.label} </strong></p>"
            @$('.save').removeClass 'disabled'

        render: () ->
            renderedContent = @template()
            @$el.html renderedContent
            @$('.project-selector').append @autocomplete.$el

            @$('.dialog').on 'hide', () =>
                @clear()

            this
