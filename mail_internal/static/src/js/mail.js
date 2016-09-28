openerp.mail_internal = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail;

    openerp_mail_followers_internal(session, mail);        // import mail_followers.js

    /**
     * ------------------------------------------------------------
     * ComposeMessage widget
     * ------------------------------------------------------------
     * 
     * This widget handles the display of a form to compose a new message.
     * This form is a mail.compose.message form_view.
     * On first time : display a compact textarea that is not the compose form.
     * When the user focuses the textarea, the compose message is instantiated.
     */
    
    mail.ThreadComposeMessage = mail.ThreadComposeMessage.extend({

        init: function () {
            this._super.apply(this, arguments);
            this.is_internal = false;
        },

        bind_events: function () {
            this._super.apply(this, arguments);
            var self = this;
            this.$('.oe_compose_internal').on('click', self.on_toggle_quick_composer);
        },

        /* Quick composer: toggle minimal / expanded mode
         */
        on_toggle_quick_composer: function (event) {
            var $input = $(event.target);
            // if clicked: call for suggested recipients
            if (event.type == 'click') {
                this.is_internal = $input.hasClass('oe_compose_internal');
            }
            return this._super(event);
        },

        on_message_post: function (event) {
            if (this.flag_post) {
                return;
            }
            if (this.do_check_attachment_upload() && (this.attachment_ids.length || this.$('textarea').val().match(/\S+/))) {
                if (this.is_internal) {
                    this.flag_post = true;
                    this.do_send_message_post([], this.is_log);
                }
                else {
                    this._super.apply(this, arguments);
                }
            }
        },

        /* do post a message and fetch the message */
        do_send_message_post: function (partner_ids, log) {
            if (this.is_internal) {
                var parent_ctx = this.parent_thread.context;
                var new_ctx = _.extend({}, parent_ctx, {
                    'mail_post_internal': true,
                });
                this.parent_thread.context = new_ctx;
            }
            var res = this._super.apply(this, arguments);
            if (this.is_internal) {
                this.parent_thread.context = parent_ctx;
            }
            return res;
        },
    });
};
