openerp_mail_followers_internal = function(session, mail) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail_followers = session.mail_followers;

    /** 
     * ------------------------------------------------------------
     * mail_followers Widget
     * ------------------------------------------------------------
     *
     * This widget handles the display of a list of records as a vertical
     * list, with an image on the left. The widget itself is a floatting
     * right-sided box.
     * This widget is mainly used to display the followers of records
     * in OpenChatter.
     */
    
    mail_followers.Followers = mail_followers.Followers.extend({

        do_follow: function () {
            this.node.attrs.context = _.extend(this.node.attrs.context || {}, {'mail_subscribe_manual': true});
            var context = new session.web.CompoundContext(this.build_context(), {});
            return this._super.apply(this, arguments);
        },
    });
};
