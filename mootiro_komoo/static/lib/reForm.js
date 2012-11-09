(function() {
  var FormView, PasswordWidget, TextAreaWidget, TextWidget, Widget, fieldTemplate, formTemplate, textTemplate, textareaTemplate;

  formTemplate = "<form action=\"\" method=\"post\" id=\"<%= formId %>\" >\n    <div>\n        <input type=\"submit\" name=\"submit\" value=\"send\" />\n    </div>\n</form>";

  fieldTemplate = "<div class=\"field-container\" for=\"<%=name%>\">\n    <label><%=label%></label>\n    <div class=\"widget-container\">\n    </div>\n</div>";

  textTemplate = "<input type=\"<%=type%>\" name=\"<%=name%>\" value=\"<%=value%>\" id=\"id_<%=name%>\" <%=attrs%> />";

  textareaTemplate = "<textarea name=\"<%=name%>\" id=\"id_<%=name%>\"><%=value%></textarea>";

  Widget = Backbone.View.extend({
    initialize: function() {
      _.bindAll(this);
      this._template = _.template(this.template);
      return this.name = this.options.name;
    },
    render: function() {
      this.$el.html(this._template(this.options));
      if (typeof this.behavior === "function") this.behavior();
      return this;
    },
    set: function(value) {
      return this.$el.find("input[name=" + this.name + "]").val(value);
    },
    get: function() {
      return this.$el.find("input[name=" + this.name + "]").val();
    }
  });

  TextWidget = Widget.extend({
    template: textTemplate,
    initialize: function() {
      var _base;
      this.options.type = 'text';
      if ((_base = this.options).attrs == null) _base.attrs = '';
      return Widget.prototype.initialize.apply(this, arguments);
    }
  });

  PasswordWidget = Widget.extend({
    template: textTemplate,
    initialize: function() {
      this.options.type = 'password';
      this.options.value = '';
      this.options.attrs = 'autocomplete="off"';
      return Widget.prototype.initialize.apply(this, arguments);
    }
  });

  TextAreaWidget = Widget.extend({
    template: textareaTemplate,
    set: function(value) {
      return this.$el.find("textarea").val(value);
    },
    get: function() {
      return this.$el.find("textarea").val();
    }
  });

  FormView = Backbone.View.extend({
    initialize: function() {
      var _ref;
      _.bindAll(this);
      this.formTemplate = _.template(formTemplate);
      if ((_ref = this.options) != null ? _ref.model : void 0) {
        this.model = this.options.model;
      }
      return this.on('submit', this.save);
    },
    render: function() {
      var args, field, id, renderedField, renderedFormTemplate, widget, _fieldTemplate, _i, _len, _ref, _ref2,
        _this = this;
      id = ((_ref = this.options) != null ? _ref.formId : void 0) || '';
      renderedFormTemplate = this.formTemplate({
        formId: id
      });
      this.$el.html(renderedFormTemplate);
      _ref2 = this.fields.slice(0).reverse();
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        field = _ref2[_i];
        args = {
          name: field.name,
          id: "id_" + field.name,
          label: field.label || field.name,
          value: field.value || ''
        };
        args = _.extend(args, field.args || {});
        widget = new field.widget(args);
        field.instance = widget;
        _fieldTemplate = _.template(fieldTemplate);
        renderedField = $(_fieldTemplate(args));
        renderedField.find('.widget-container').html(widget.render().el);
        this.$el.find('form').prepend(renderedField);
        if (this.model) this.set(this.model.toJSON());
      }
      this.$el.find('form').submit(function(evt) {
        evt.preventDefault();
        return _this.trigger('submit');
      });
      return this;
    },
    save: function() {
      var _this = this;
      return this.model.save(this.get(), {
        success: function(model, resp) {
          _this.cleanErrors();
          return _this.trigger('success', resp);
        },
        error: function(model, resp) {
          console.log(resp);
          resp = JSON.parse(resp.responseText);
          _this.errors(resp.errors || {});
          return _this.trigger('error', resp);
        }
      });
    },
    errors: function(vals) {
      var field, msg, name;
      if (this._errors == null) this._errors = {};
      if (vals) {
        this._errors = _.extend(this._errors, vals);
        for (name in vals) {
          msg = vals[name];
          field = this.$el.find(".field-container[for=" + name + "]");
          field.find("#id_" + name).addClass('error');
          field.find("label").addClass('error');
          if (!field.find("small.error").length) {
            field.find(".widget-container").after("<small class='error'>" + msg + "</smalll>");
          }
        }
      } else {
        return this._errors;
      }
    },
    cleanErrors: function() {
      this.$el.find('small.error').remove();
      return this.$el.find('.error').removeClass('error');
    },
    get: function(fieldName) {
      var field, vals, _i, _len, _ref;
      if (fieldName == null) fieldName = '__all__';
      if (fieldName === '__all__') {
        vals = {};
        _ref = this.fields;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          field = _ref[_i];
          vals[field.name] = field.instance.get();
        }
        return vals;
      } else {
        field = _.find(this.fields, function(f) {
          return f.name === fieldName;
        });
        return field.instance.get();
      }
    },
    set: function(vals) {
      var field, key, value, _ref, _results;
      if (vals == null) vals = {};
      _results = [];
      for (key in vals) {
        value = vals[key];
        field = _.find(this.fields, function(f) {
          return f.name === key;
        });
        _results.push(field != null ? (_ref = field.instance) != null ? typeof _ref.set === "function" ? _ref.set(value) : void 0 : void 0 : void 0);
      }
      return _results;
    }
  });

  window.ReForm = {
    Form: FormView,
    Widget: Widget,
    commonWidgets: {
      TextWidget: TextWidget,
      PasswordWidget: PasswordWidget,
      TextAreaWidget: TextAreaWidget
    }
  };

  if (typeof define === "function" && define.amd) {
    define(function() {
      return window.ReForm;
    });
  }

}).call(this);
