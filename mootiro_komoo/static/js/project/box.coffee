define [
    'jquery',
    'underscore',
    'backbone',
    'project/add_dialog'
    'text!templates/project/_box.html',
    'utils'
], ($, _, Backbone, AddDialog, tplt) ->
    'use strict'

    ProjectItemView = Backbone.View.extend
        tagName: 'li'

        initialize: () ->
            _.bindAll this, 'render'
            @model.bind 'change', @render, this
            @model.bind 'destroy', @remove, this

        render: () ->
            @$el.html "<a href=\"#{@model.get('view_url')}\">#{@model.get('name')}</a>"
            this

    BoxView = Backbone.View.extend
        className: 'project_box'

        events:
            'click .add': 'onAddBtnClick'

        initialize: () ->
            _.bindAll this, 'render'
            @template = _.template tplt

            @collection?.bind 'add', @addOne, this
            @collection?.bind 'reset', @render, this

            @addDialog = new AddDialog(model: @model).render()
            @addDialog.on 'saved', (project) =>
                # TODO: i18n me
                flash "Adicionado ao projeto #{project.get('name')}"
                @collection.add project
                @addDialog.close()
            @addDialog.on 'failed', (project, msg) =>
                # TODO: i18n me
                flash "Falhou ao adicionar ao projeto #{project.get 'name'}: #{msg}"

        addOne: (project) ->
            view = new ProjectItemView model: project
            @$('.list').append view.render().el

        addAll: () ->
            @collection?.each (project) =>
                @addOne project

        openAddDialog: () ->
            @addDialog.open()

        onAddBtnClick: () ->
            @openAddDialog()
            false

        render: () ->
            renderedContent = @template
                projects: @collection
            @$el.html renderedContent

            @addAll()

            this

    BoxView
