# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

RELATIONS = {
    # 'relation_type_name': (from_1_to_2, from_2_to_1),

    'ownership': (
        _('owns'), _('is owned by')
    ),
    # possui, pertence à

    'participation': (
        _('participates in'), _('has as participant')
    ),
    # participa de, tem como participante

    'partnership': (
        _('partners with'), _('partners with')
    ),
    # é parceiro de, é parceiro de

    'grants': (
        _('gives a grant to'), _('receives a grant from')
    ),
    # finacia, recebe um financiamento de

    'certification': (
        _('certifies'), _('is certified by')
    ),
    # certifica, é certificada por

    'students attendance': (
        _('attends students from'), _('attends')
    ),
    # students attendance, attends students from - atende alunos de

    'directing people': (
        _('directs people to'), _('receives people from')
    ),
    # encaminha atendidos para, recebe encaminhamentos de atendidos de

    'volunteers': (
        _('recruits volunteers for'), _('receives volunteers from')
    ),
    # recruta voluntários para, recebe voluntários de

    'support': (
        _('supports'), _('is supported by')
    ),
    # suporta, recebe suporte

    'representation': (
        _('represents'), _('is represented by')
    ),
    # representa, é representado por

    'membership': (
        _('is a member of'), _('has as member')
    ),
    # é membro de, tem como membro

    'supply': (
        _('supplies to'), _('buys from')
    ),
    # fornece para, compra de

    'council': (
        _('is board member of'), _('has as board member')
    ),
    # é conselheiro de, tem como conselheiro
}
