openerp.project_planning_tool_team = function(instance){
    var QWeb = instance.web.qweb;

    instance.web.client_actions.add('project.planning.ui', 'instance.project_planning_tool_team.ProjectWidget');
    instance.project_planning_tool_team.ProjectWidget = instance.web.Widget.extend({
        jqueryui_object: 'datetimepicker',
        template : 'Project-Screen',
        number_of_color_schemes: 10,
        type_of_date : "datetime",

        init: function(){
            this._super();
            var self = this;
            this.res_lang_dataset = new instance.web.DataSetSearch(this, 'res.lang', {}, [['code', '=', this.session.user_context.lang]]);
            this.res_lang_dataset.read_slice(([]), {}).then(function(records) {
                self.current_user_lang = records[0];
            });
            this.currently_dragging = {};
        },

        build_widget: function() {
            return new instance.web.DateTimeWidget(this);
        },

        format_client: function(v) {
            return instance.web.format_value(v, {"widget": this.type_of_date});
        },

        parse_client: function(v) {
            return instance.web.parse_value(v, {"widget": this.type_of_date});
        },

        start: function(){
            var self = this;
            self.load = true;

            self.datestart_widget = this.build_widget();
            self.datestart_widget.appendTo(this.$el.find(".datetimepicker_date_start"));

            self.dateto_widget = this.build_widget();
            self.dateto_widget.appendTo(this.$el.find(".datetimepicker_date_to"));

            var today = new Date();
            var startOfWeek = instance.web.date_to_str(moment().startOf('week').toDate()) +" 00:00:00";
            var endOfWeek   = instance.web.date_to_str(moment().endOf('week').toDate()) +" 23:59:00";
            
            self.datestart_widget.set({'value': startOfWeek });
            self.datestart_widget.$input.val(startOfWeek ? startOfWeek : '');
//
            self.dateto_widget.set({'value': endOfWeek });
            self.dateto_widget.$input.val(endOfWeek ? endOfWeek : '');

            date_start = self.datestart_widget.get_value();
            date_to = self.dateto_widget.get_value();

            self.show_project(self.datestart_widget.get_value(),self.dateto_widget.get_value());

            //bind click event for search button
            $("#search_button").click(function(){
                self.load = false;
                var date_start = instance.web.auto_str_to_date(self.datestart_widget.get_value());
                var startOfWeek = instance.web.date_to_str(date_start);
                date_start = self.format_client(date_start);
                self.datestart_widget.$input.val(date_start);
               // date_start = self.datestart_widget.get_value()
                
                var date_to = instance.web.auto_str_to_date(self.dateto_widget.get_value());
                var endOfWeek = instance.web.date_to_str(date_to);
                date_to = self.format_client(date_to);
                self.dateto_widget.$input.val(date_to);
                date_to = self.dateto_widget.get_value();
                
                self.show_project(startOfWeek,endOfWeek);
            });

            //bind click event for back button button
            $(".back_img").click(function(){
                self.load = false;
                var date_start = instance.web.auto_str_to_date(self.datestart_widget.get_value());
                date_start.add(-7).day();
                if(date_start.getDay() == 1){
                    date_start.add(-1).day();
                }else if( date_start.getDay() == 2){
                    date_start.add(-2).day();
                }else if( date_start.getDay() == 3){
                    date_start.add(-3).day();
                }else if( date_start.getDay() == 4){
                    date_start.add(-4).day();
                }else if( date_start.getDay() == 5){
                    date_start.add(-5).day();
                }
                else if( date_start.getDay() == 6){
                    date_start.add(-6).day();
                }
                var startOfWeek = instance.web.date_to_str(date_start);
                date_start = self.format_client(date_start);
                self.datestart_widget.$input.val(date_start)
                .change()
                .focus();
                var date_to = instance.web.auto_str_to_date(self.datestart_widget.get_value());
                date_to.add(6).day();
                if(date_to.getDay() == 1){
                    date_to.add(5).day();
                }else if( date_to.getDay() == 2){
                    date_to.add(4).day();
                }else if( date_to.getDay() == 3){
                    date_to.add(3).day();
                }else if( date_to.getDay() == 4){
                    date_to.add(2).day();
                }else if( date_to.getDay() == 5){
                    date_to.add(1).day();
                }
                var endOfWeek = instance.web.date_to_str(date_to);
                date_to = self.format_client(date_to);
                self.dateto_widget.$input.val(date_to)
                .change()
                .focus();
                self.show_project(startOfWeek,endOfWeek);
               // self.show_project(self.datestart_widget.get_value(),self.dateto_widget.get_value())
            });

            //bind click event for forward button
             $(".forward_img").click(function(){
                self.load = false;
                var date_start = instance.web.auto_str_to_date(self.dateto_widget.get_value());
                if(date_start.getDay() == 1){
                    date_start.add(6).day();
                }else if( date_start.getDay() == 2){
                    date_start.add(5).day();
                }else if( date_start.getDay() == 3){
                    date_start.add(4).day();
                }else if( date_start.getDay() == 4){
                    date_start.add(3).day();
                }else if( date_start.getDay() == 5){
                    date_start.add(2).day();
                }else if(date_start.getDay() == 6){
                    date_start.add(1).day();
                }
                var startOfWeek = instance.web.date_to_str(date_start);
                date_start = self.format_client(date_start);
                self.datestart_widget.$input.val(date_start)
                .change()
                .focus();
                var date_to = instance.web.auto_str_to_date(self.dateto_widget.get_value());
                date_to.add(-1).day();
                date_to.add(7).day();
                 if(date_to.getDay() == 1){
                    date_to.add(5).day();
                }else if( date_to.getDay() == 2){
                    date_to.add(4).day();
                }else if( date_to.getDay() == 3){
                    date_to.add(3).day();
                }else if( date_to.getDay() == 4){
                    date_to.add(2).day();
                }else if( date_to.getDay() == 5){
                    date_to.add(1).day();
                }
                var endOfWeek = instance.web.date_to_str(date_to);
                date_to = self.format_client(date_to);
                self.dateto_widget.$input.val(date_to)
                .change()
                .focus();
                self.show_project(startOfWeek,endOfWeek);
                //self.show_project(self.datestart_widget.get_value(),self.dateto_widget.get_value())
            });
        },

        show_project: function(date_start,date_to){
            var self = this;
            var normalize_format = function (format) {
                return Date.normalizeFormat(instance.web.strip_raw_chars(format));
            };
            if(! date_start){
                alert("Pleas Enter Start Date!");
            }else if(! date_to){
                        alert("Please Enter End Date!");
            }else{
                if($(".project_data table")){
                    $(".project_data table").remove();
                    $(".project_data div").remove();
                }
                this.project_task_dataset = new instance.web.DataSetSearch(this, 'project.task', {}, [['date_start', '>=', date_start], ['date_end', '<=', date_to]]);
                this.project_task_dataset.read_slice(([]), {}).then(function(records) {
                    if(! records.length){
                        alert("Record Not Found !");
                        return false;
                    }else{
                        self.users = [];
                        self.teams = [];
                        _.each(records, function(rec){
                            var flag = true;
                           /* _.each(self.users, function(user){
                                if(user[0] == rec.user_id[0]){
                                    flag = false
                                }
                            })*/
                             _.each(self.teams, function(team){
                                if(team[0] == rec.team_id[0]){
                                    flag = false;
                                }
                            });
                            if(flag){
                                self.users.push(rec.user_id);
                                self.teams.push(rec.team_id);
                            }
                        });
                        //Create User header and add display
                        $(".project_data").html(QWeb.render('Project-User',{'users': self.teams}));
                        //find total days beetween two date
                        var oneDay = 24*60*60*1000; // hours*minutes*seconds*milliseconds
                        
                        var firstDate = instance.web.auto_str_to_date(date_start);
                        var secondDate = instance.web.auto_str_to_date(date_to);
                        var diffDays = Math.round(Math.abs((firstDate.getTime() - secondDate.getTime())/(oneDay)));
                        var total_week = parseInt(diffDays/7);
                        var datas = [];
                        var week_data = [];
                        var week_index = 0;
                        var increase_date = instance.web.auto_str_to_date(date_start);
                        var week_count = 1;
                        for(var day = 1; day <= diffDays + 2; day++){
                            if(day % 8 == 0){
                                week_data.push(["Week_"+week_count, datas]);
                                datas = [];
                                week_count ++;
                            }
                            curr_data = increase_date.getFullYear() +"-"+ ("0" + (increase_date.getMonth() + 1)).slice(-2) +"-"+ ("0" + increase_date.getDate()).slice(-2);
                            var user_data = [];
                           /* _.each(self.users, function(user){
                                var day_data = []
                                _.each(records, function(rec){
                                    var rec_date = new Date.parse(rec.date_start)
                                    if(rec.user_id[0] == user[0] && (rec_date.getDate() == increase_date.getDate() && rec_date.getMonth() == increase_date.getMonth() && rec_date.getFullYear() == increase_date.getFullYear())){
                                        var value = instance.web.auto_str_to_date(rec.date_deadline)
                                        if(value){
                                            rec.date_deadline = value.toString(normalize_format(self.current_user_lang.date_format))
                                        }
                                        day_data.push(rec)
                                    }
                                })
                                user_data.push([user,day_data])
                            })*/
                            _.each(self.teams, function(team){
                                var day_data = [];
                                _.each(records, function(rec){
                                    var rec_date = new Date.parse(rec.date_start);
                                    if(rec.team_id[0] == team[0] && (rec_date.getDate() == increase_date.getDate() && rec_date.getMonth() == increase_date.getMonth() && rec_date.getFullYear() == increase_date.getFullYear())){
                                        var value = instance.web.auto_str_to_date(rec.date_deadline);
                                        if(value){
                                            rec.date_deadline = value.toString(normalize_format(self.current_user_lang.date_format));
                                        }
                                        day_data.push(rec);
                                    }
                                });
                                user_data.push([team,day_data]);
                            });
                            var value = instance.web.auto_str_to_date(curr_data);
                            curr_data = value.toString(normalize_format(self.current_user_lang.date_format));
                            datas.push([curr_data, user_data]);
                            increase_date = new Date(increase_date.setDate(increase_date.getDate()+1));
                        }
                        $(".week_project_table").html(QWeb.render('week-data',{'week_datas': week_data, 'users':self.users,'teams':self.teams}));
                        self.setup_color_picker();
                        var $records = self.$el.find('.oe_project_task_record');
                        var $columns = self.$el.find('.oe_kanban_column_view');
                        $records.addClass( "ui-widget-header ui-corner-all" )
                        .prepend( "<span class='ui-icon ui-icon-plusthick portlet-toggle'></span><ul class='oe_dropdown_menu'><li><ul class='oe_kanban_colorpicker' data-field='color'/></li></ul>");
                        self.setup_color_picker();
                        $( ".portlet-toggle" ).click(function() {
                            var icon = $( this );
                            icon.toggleClass( "ui-icon-minusthick ui-icon-plusthick" );
                            icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_toggle" ).toggle();
                            icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_menu" ).toggle();
                            if (icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_toggle" ).hasClass("oe_opened")) {
                                icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_toggle" ).removeClass( "oe_opened" );
                            }else{
                                icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_toggle" ).addClass( "oe_opened" );
                            }
                            if (icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_menu" ).hasClass("oe_opened")) {
                                icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_menu" ).removeClass( "oe_opened" );
                            }else{
                                icon.closest( ".oe_project_task_record" ).find( ".oe_dropdown_menu" ).addClass( "oe_opened" );
                            }
                        });
                        $columns.sortable({
                            handle : '.oe_kanban_draghandle',
                            start: function(event, ui) {
                                self.old_team = $(".week_project_table tr td:eq("+$(ui.item).closest("td").index()+')');
                                self.currently_dragging.index = ui.item.parent().children('.oe_kanban_record').index(ui.item);
                                self.currently_dragging.group = ui.item.parents('.oe_kanban_column_view:first').data('widget');
                                ui.item.find('*').on('click.prevent', function(ev) {
                                    return false;
                                });
                                ui.placeholder.height(ui.item.height());
                            },
                            revert: 150,
                            stop: function(event, ui) {
                                var record = ui.item.data('widget');
                                self.new_team = $(".week_project_table tr td:eq("+$(ui.item).closest("td").index()+')');
                                self.drag_date = $(ui.item).closest('tr').find('.day_label')[0].textContent.trim() + " 10:10:10";
                                self.drag_date = self.parse_client(self.drag_date);
                                self.current_record_id = $(ui.item).children("div").data("id");
                                if(self.new_team && self.new_team != self.old_team){
                                    self.project_task_dataset = new instance.web.DataSetSearch(self, 'project.task', {}, []);
                                    self.project_task_dataset.write(parseInt(self.current_record_id), {'team_id':parseInt(self.new_team.attr("id")),'date_start':self.drag_date});
                                }
                                self.setup_color_picker();
                                setTimeout(function() {
                                    // A bit hacky but could not find a better solution for Firefox (problem not present in chrome)
                                    // http://stackoverflow.com/questions/274843/preventing-javascript-click-event-with-scriptaculous-drag-and-drop
//                                  ui.item.find('*').off('click.prevent');
                                }, 0);
                             },
                             scroll: false
                        });
                        $columns.sortable( "refresh" );
                        $columns.sortable({ connectWith: $columns });
                        self.$el.find(".oe_fold").click(function(event){
                            self.oe_fold(this);
                        });
                        _.each(self.$el.find('.oe_kanban_card'),function(card){
                            $(card).dblclick(function(){
                                if($(this).data('project_id')){
                                    id = $(this).data('project_id').split(',')[0];
                                    var model = "project.project";
                                    var view_type = "form";
                                    window.location.replace("#id="+ parseInt(id)+"&view_type="+view_type +"&model="+model);
                                }
                                
//                                self.project_task_dataset = new instance.web.DataSetSearch(self, 'project.task', {}, []);
//                                self.project_task_dataset.call("view_task",[[]]).done(function(action_id){
//                                    //document.location.assign("#id="+ parseInt(id)+"&view_type="+view_type +"&model="+model + "&action=" + action_id)
//                                    window.location.replace("#id="+ parseInt(id)+"&view_type="+view_type +"&model="+model + "&action=" + action_id);
//                                });
                            });
                        });
                    }
                });
            }
        },

        oe_fold: function(ui){
            var index = $(ui).closest("td").index();
            $(".week_project_table").find("td:eq("+index+") div").toggleClass("oe_toggel");
        },

        setup_color_picker: function() {
            var self = this;
            var $el = this.$el.find('ul.oe_kanban_colorpicker');
            if ($el.length) {
                $el.html(QWeb.render('KanbanColorPickerExtended', {
                    widget: this
                }));
                $el.on('click', 'a', function(ev) {
                    ev.preventDefault();
                    var color_field = $(this).parents('.oe_kanban_colorpicker').first().data('field') || 'color';
                    var data = {};
                    data[color_field] = $(this).data('color');
                    var color = parseInt($(this).data('color'));
                    self.current_record_id = $(this).closest("div.oe_project_task_record").data("id");
                    self.project_task_dataset.write(parseInt(self.current_record_id), {'color':color});
                    var date_start = instance.web.auto_str_to_date(self.datestart_widget.get_value());
                    var startOfWeek = instance.web.date_to_str(date_start);
                    var date_to = instance.web.auto_str_to_date(self.dateto_widget.get_value());
                    var endOfWeek = instance.web.date_to_str(date_to);
                    if(self.load){
                       setTimeout(function() {
                           self.show_project(self.datestart_widget.get_value(),self.dateto_widget.get_value());
                       },100);
                    }else{
                       setTimeout(function() {
                           self.show_project(startOfWeek,endOfWeek);
                       },100);
                    }
                });
            }
        },
    });
};