var $id_org_name_autocomplete = $('#id_org_name_autocomplete');
var $id_org_name = $('#id_org_name');
var $organization_fields = $('#organization_fields');
var $branch_fields = $('#branch_fields');
var $form_organization_btns = $('#form_organization_btns');
var $submit_btn = $('#submit_btn');
var $id_form_control = $('#id_form_control');
var forms;

/* checks if we are acessing the map from the button, or the map */
var btn_mode = Boolean(getUrlVars().frommap);

if ( ! btn_mode ){
$organization_fields.hide();
$branch_fields.hide();
$form_organization_btns.hide();


$id_org_name_autocomplete.autocomplete({
    source: "/organization/search_by_name/",
    focus: function(event, ui) {
        $id_org_name_autocomplete.val(ui.item.label);
        return false;
    },
    select: function(event, ui) {
        $id_org_name_autocomplete.val(ui.item.label);
        $id_org_name.val(ui.item.value);

        // org ja exite -> somente branch
        $branch_fields.fadeIn('slow');
        $organization_fields.hide();
        $form_organization_btns.fadeIn('slow');
        forms = ['branch'];

        return false;
    },
    change: function(event, ui) {
        if(!ui.item || ! $id_org_name_autocomplete.val()){
            // Nova org ->  (branch + org)
            $organization_fields.fadeIn('slow');
            $branch_fields.fadeIn('slow');
            $form_organization_btns.fadeIn('slow');
            forms = ['organization', 'branch'];
        }
    }
 });

$submit_btn.click(function(evt){
    $id_form_control.val(forms.join('|'));
});

} else {

    $branch_fields.hide();
    $id_form_control.val('organization');
}
