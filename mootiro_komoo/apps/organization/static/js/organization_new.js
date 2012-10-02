var change_msg = function(msg){
    if($('#org-div-progress .alert').is(':hidden')){
        $('#org-div-progress .alert').slideDown();
    }
    var $msg = $('#org-div-progress .alert .msg');
    $msg.fadeOut('100', function(){
        $msg.html(msg);
        $msg.fadeIn('100');
    })
};

var change_percent = function(percent){
    $('#org-div-progress .percent').html(
        percent + '% ' + gettext('complete'));
};

var change_step = function(step){
    var percent, msg;

    for (var i = 1; i < 5 ; i++) {
        $('.step_' + i).hide();
    }
    $('.step_' + step).show();
    percent = Math.round(step * 33.33 - 33.33);
    $('.progress .bar').css('width', '' + percent + '%');

    if (step === 1){
        $('.step_1_row_1').show();
        $('.step_1_row_2').hide();
        $('.step_1_row_3').hide();
    } else if (step === 4) {
        // change_msg('Parabéns você concluiu o processo de adição de uma organização/filial');
        change_msg(gettext('Congratulations, you have concluded the organization/branch addition process'));
    }
    change_percent(percent);
    window.scrollTo(0, 0);
};
$(function(){
    change_step(1);
    // change_msg('Forneça o nome da organização para verificarmos se ela ainda não foi cadastrada no sistema.');
    change_msg(gettext("Provide the organization name so we can verify if it's already registered on our system"));
    $('a.close').click(function(){
        $(this).parent().slideUp();
    });

    $('#name_verify').click(function(){
        $.post(
            '/organization/verify_name/',
            {'org_name': $('#id_org_name_autocomplete').val()},
            function(data){
                var msg, step;
                if (data.exists){
                    // change_msg('Esta organização já existe. Deseja adicionar uma filial?');
                    change_msg(gettext('This organization already exists. Do you want to add a branch?'));
                    $('.step_1_row_1').hide();
                    $('.step_1_row_2').show();
                    $('#form_branch #id_branch_organization').val(data.id);
                    $('#btn_concluir').attr('id', data.id);
                } else {
                    // change_msg('Esta organização ainda não foi cadastrada. Deseja adicionar esta organização?');
                    change_msg(gettext("This organization is not registered yet. Do you want to add this organization?"));
                    $('.step_1_row_1').hide();
                    $('.step_1_row_3').show();
                }

            },
            'json');
    });

    $('#btn_add_filial').click(function(){
        change_step(3);
        // change_msg('Entre com os dados da filial que você marcou no mapa');
        change_msg(gettext('Enter with the data from the branch you have marked on map'));
        var name = $('#id_org_name_autocomplete').val();
        $('#id_filial_org_name').val(name);
    });

    $('#btn_add_org').click(function(){
        change_step(2);
        // change_msg('Entre com os dados da Organização que detém a unidade que você marcou no mapa.')
        change_msg(gettext('Enter with the data from the Organization which owns the branch you have marked on map.'));
        var name = $('#id_org_name_autocomplete').val();
        $('#form_organization #id_name').val(name);
        $('#id_filial_org_name').val(name);
    });

    $('.step_1_cancel').click(function(){
        change_step(1);
        // change_msg('Forneça o nome da organização para verificarmos se ela ainda não foi cadastrada no sistema.');
        change_msg(gettext("Provide the organization name so we can verify if it's already registered on our system"));

    });

    $('#btn_concluir').click(function(){
        var id = $(this).attr('id');
        url =  dutils.urls.resolve('view_organization', {'id': id });
        window.location.pathname =  url;
    });

    $('#form_organization').ajaxform({
        onSuccess: function(data){
            change_step(3);
            // change_msg('Parabéns, sua organização foi salva corretamente. Por favor, agora preencha os dados para a filial que você marcou no mapa');
            change_msg(gettext('Congratulations, your organization was successfully saved. Please, now add the data from the branch you have marked on the map'));
            $('#form_branch #id_branch_organization').val(data.obj.id);
            $('#id_filial_org_name').val(data.obj.name);
            $('#btn_concluir').attr('id', data.obj.id);
        }
    });
    $('#form_branch').ajaxform({
        onSuccess: function(data){
            change_step(4);
        }
    });

    $('#form_organization').komooFormHintBoxes({
        'name': {
          hint: 'Coloque o nome da organização.'
        },
        'description': {
          top: '45%',
          hint: 'Coloque detalhes da organização e como ela atua na comunidade.'
        },
        'community':{
          hint: 'Coloque as comunidades que a organização atua ou atende.',
          top: '-8px'
        },
        'link': {
            hint: 'Coloque o endereço do site da organização. Se ela não tiver, ou você não achar, tudo bem, não é obrigatório.',
            top: '-15px'
        },
        'contact': {
          hint: 'Coloque aqui os contatos da organização, telefones, endereço, pessoas que podemos conversar...',
          top: '25%'
        },
        'target_audiences': {
          hint: 'Coloque o tipo de pessoas que essa organização busca atingir na comunidade.',
          top: '-12px'
        },
        'categories':{
            hint: 'Escolha em que área a organização atua, pode-se escolher mais de uma.',
            top: '45%'
        },
        'tags': {
          hint: 'Coloque palavras que ajudem a ilustrar a organização, tal como "escola", "educação", "meio-ambiente"',
          top: '-12px'
        },
        'files': {
          hint: 'Você pode carregar fotos da sua organização',
          top: '40%'
        },
        'logo': {
          hint: 'neste campo voce pode subir um logo da sua organização ou optar por usar uma imagem correspondente a uma das categorias que você marcou acima. Lembre-se primeiro de escolher as categorias para que as imagens apareçam aqui.',
          top: '-40px'
        }
    });

    $('#form_branch').komooFormHintBoxes({
        'branch_name': {
          hint: 'Coloque o nome da unidade que você marcou no mapa.',
          top: '-8px'
        },
        'branch_info': {
          top: '40%',
          hint: 'Coloque algumas informações sobre essa unidade (por exemplo: se ela é a sede, ou possui um propósito específico, etc).'
        }
    });
})
