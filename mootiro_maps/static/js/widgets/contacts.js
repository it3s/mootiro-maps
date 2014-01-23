// ContactsWidget Module
var ContactsWidget = {
  updateValues: function(module) {
    // change events callback
    var contacts = {};
    module.contactsListField.find(".contact-kv input").each(function(index, el) {
      el = $(el);
      contacts[el.data("key")] = el.val() === "" ?  null : el.val();
    });

    // update values as parsed JSON on module.field
    module.field.val(JSON.stringify(contacts));
  },

  listen: function() {
    // listen for change events
    var module = this;
    module.contactsListField.find(".contact-kv input").change(function() {
      module.updateValues(module);
    });
  },

  onLoad: function() {
    this.field = $("#id_contacts");
    this.contactsListField = $(".contacts-list");

    var initialValues = JSON.parse(this.field.val());

    this.loadInitialValues(initialValues);
    this.listen();
  },

  getKeyName: function(key) {
    return this.field.data("key-names")[key];
  },

  keyOrder: function() {
    return [
      'address',
      'compl',
      'city',
      'postal_code',
      'phone',
      'facebook',
      'email',
      'twitter',
      'site',
      '---',
    ];
  },

  loadInitialValues: function(initialValues) {
    var module = this;

    _.each(module.keyOrder(), function(key) {
      var value = initialValues[key];
      module.renderKeyValuePair(key, module.getKeyName(key), value);
    });
  },

  renderKeyValuePair: function(key, keyName, value) {
    console.log("rendering contacts: key=%s value=%s", key, value);
    this.contactsListField.append("" +
      "<div class=\"contact-kv\">" +
        "<label>" + keyName + "</label>" +
        "<input type='text' value='" + (value || "") + "' data-key='" + key + "' />" +
      "</div>"
    );
  },


};

$(function() {
  ContactsWidget.onLoad();
});
