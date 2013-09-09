
$ = jQuery

#
# ======== Backbone => MVC for signatures settings =========
#
window.Signature = Backbone.Model.extend
    imageName: () ->
        "/static/img/updates-page/#{@model_name}-feed.png"

    toJSON: (attr) ->
        defaultJSON = Backbone.Model.prototype.toJSON.call this, attr
        _.extend defaultJSON, {
            imageName: @imageName
        }

    deleteSignature: () ->
        if confirm(gettext 'Are you sure you want to delete your signature for this object?')
            self = this
            $.post(
                dutils.urls.resolve('signature_delete'),
                {id: @get 'signature_id'},
                (data) ->
                    self.trigger 'deleteSignature', self
                ,
                'json'
            )

window.SignatureView = Backbone.View.extend
    className: 'signature'
    events:
        'click .cancel-subscription-btn': 'cancelSubscription'

    initialize: () ->
        _.bindAll this, 'render', 'cancelSubscription', 'remove'
        @template = _.template $('#signature-template').html()
        @model.bind 'deleteSignature', @remove

    render: () ->
        renderedContent = @template @model.toJSON()
        $(@el).html renderedContent
        this

    cancelSubscription: () ->
        @model.deleteSignature()
        this

    remove: () ->
        $(@el).slideUp 300, () ->
            $(this).remove()
        this


window.SignaturesList = Backbone.Collection.extend
    model: Signature


window.SignaturesListView = Backbone.View.extend
    events:
        'click #signatures-manage-btn': 'digestOptions'
        'click #digest-options-save': 'digestOptionsSave'

    initialize: () ->
        _.bindAll this, 'render', 'digestOptions'

        @template = _.template $('#signatures-list-collection').html()
        @collection.bind 'reset', @render

    render: () ->
        $(@el).html @template({})
        $signatures = this.$ '.signatures-list'
        @digestModal = this.$ '#digest-options-modal'
        @digestForm = this.$ '#form-digest'

        collection = @collection
        collection.each (sign) ->
            view = new SignatureView
                model: sign
                # collection: collection
            $signatures.append view.render().el

        self = this
        @digestForm.ajaxform
            clean: false
            onSuccess: () ->
               self.digestModal.modal 'hide'
        this

    digestOptions: () ->
        @digestModal.modal 'show'
        this

    digestOptionsSave: () ->
        @digestForm.submit()


# jQuery -> on document ready
$ () ->

    #
    #=========  Public Settings Tab ==========
    #
    $('#form-profile').ajaxform
        clean: false
        onSuccess: (data) ->
            $messageBox = $ '.form-message-box'
            if $messageBox.length
                $messageBox.remove()
            msgTemplate = _.template $('#form-message-box').html()
            renderedContent = msgTemplate
                msg: gettext 'Seus dados públicos foram salvos com sucesso!'

            $('#form-profile .form-actions').before renderedContent
            $('#form-profile .alert').fadeIn()
            false


    $('#form-profile').komooFormHintBoxes
        'contact':
            hint: 'Este Contanto ficará visível para outros usuários do MootiroMaps!'
            top: '30%'


    # message box close when x button is clicked
    $('.alert .close').live 'click', () ->
        $(this).parent().slideUp()

    #
    #========== Personal Settings Tab ================
    #
    $('#form-personal').ajaxform
        clean: false
        onSuccess: (data) ->
            $messageBox = $ '.form-message-box'
            if $messageBox.length
                $messageBox.remove()
            msgTemplate = _.template $('#form-message-box').html()
            renderedContent = msgTemplate
                msg: gettext 'Seus dados pessoais foram salvos com sucesso!'

            $('#form-personal .form-actions').before renderedContent
            $('#form-personal .alert').fadeIn()
            false

    #
    #=========== Signatures Settings Tab ==============
    #
    loadedSignatures = new SignaturesList()
    loadedSignatures.reset window.KomooNS.signatures

    signaturesListView = new SignaturesListView
        collection: loadedSignatures

    $('.signatures-list-wrapper').append signaturesListView.render().el

