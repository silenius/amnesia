;(function(ns) {
    var Bbpf = ns.Bbpf = {};

    Bbpf.config = {};
    Bbpf.utils = {};

    /*************************************************************************
        Helper functions (shortcuts)
    **************************************************************************/

    function site_url() {
        var url = Array.prototype.slice.call(arguments);
        url.splice(0, 0, Bbpf.config.urls.prefix);
        return url.join('/').replace(/\/{2,}/, '/');
    }

    function _browser_callback(field_name, url, type, win) {
        //window.console.log("Field_Name: " + field_name + " | URL: " + url + " | Type: " + type + " | Win: " + win);

        var browser_modal = jQuery('#browser_modal'),
            _folder_main = Yeti.Element('browser-main'),
            _folder_pagination = Yeti.Element('browser-pagination'),
            _folder_navigation = Yeti.Element('browser-nav'),
            pagination = new Bbpf.Pagination({}),
            browser = new Bbpf.FolderController({
                url : site_url('1/browse'),
                components : {
                    main : new Bbpf.Component({
                        container: _folder_main
                    }),
                    pagination: new Bbpf.PaginationComponent({
                        container: _folder_pagination,
                        pagination: pagination
                    }),
                    navigation: new Bbpf.NavigationComponent({
                        container: _folder_navigation
                    })
                },
                parameters : {
                    framed : true,
                    sort_folder_first: true,
                    options : ['tinymce_' + type]
                }
            }); // var

        if (type == 'image') {
            browser.parameters.filter_types = ['folder', 'file'];
            browser.parameters.filter_mime = ['image/*'];
            browser.parameters.display = 'thumbnail';
        } else if (type == 'file') {
            browser.parameters.display = 'icon';
        } else if (type == 'media') {
            browser.parameters.display = 'icon';
            browser.parameters.filter_types = ['folder', 'file'];
            browser.parameters.filter_mime = ['video/*'];
        }

        browser.load();
        browser_modal.modal('show');

        pagination.dispatcher.add('pagination_change', function() {
            browser.refresh({
                limit: this.get('limit'),
                offset: this.get('offset')
            });
        });

        browser.dispatcher.add('after_load_success', function() {

            /* Add handlers on the <button> tags. They're used to select the
               object for insertion in the TinyMCE editor */

            var select = Yeti.Element(this.components.main.container).getElementsByTagName('button'),
                field = Yeti.Element(field_name);

            for (var i=0, _len = select.length; i<_len; i++) {
                (function(elem) {
                    elem.addEventListener('click', function(e) {
                        var obj_meta = JSON.parse(this.getAttribute('data-obj'));

                        field.value = obj_meta.id;

                        switch(type) {
                            case 'image':
                            case 'media':
                                field.value += '/download';
                                break;
                            case 'file':
                                if (obj_meta.type.name == 'file') {
                                    field.value += '/download';
                                }
                                break;
                        }

                        browser_modal.modal('hide');
                    });
                })(select[i]);

            }

            /* Add handlers on the folder objects */

            var links = Yeti.Element(this.components.main.container).getElementsByTagName('a');

            for (var i=0, _len = links.length; i<_len; i++) {
                (function(elem) {
                    elem.addEventListener('click', function(e) {
                        e.preventDefault();

                        var obj_meta = JSON.parse(this.getAttribute('data-obj'));

                        if (obj_meta.type.name == 'folder') {
                            browser.url = site_url(obj_meta.id, '/browse');
                            browser.load();
                        }
                    });
                })(links[i]);
            }

            /* Add handlers on the navigation bar */

            var links = Yeti.Element(this.components.navigation.container).getElementsByTagName('a');

            for (var i=0, _len = links.length; i<_len; i++) {
                (function(elem) {
                    elem.addEventListener('click', function(e) {
                        e.preventDefault();

                        var obj_meta = JSON.parse(this.getAttribute('data-obj'));

                        browser.url = site_url(obj_meta.id, '/browse');
                        browser.parameters.offset = 0;
                        browser.load();
                    });
                })(links[i]);
            }
        });

        return false;
    }

    // Create/initialize a preconfigured editor
    Bbpf.utils.init_tinyMCE = function(params) {

        /* VERY IMPORTANT !! document_base_url MUST end with a "/" (otherwise
           TinyMCE inserts broken links) */
        var document_base_url = Bbpf.config.urls.host + Bbpf.config.urls.prefix;
        if (document_base_url.charAt(document_base_url.length - 1) != '/') {
            document_base_url += '/';
        }

        if (!/https?:\/\//.test(document_base_url)) {
            document_base_url += 'http://'
        }

        /* All available plugins */
        var plugins = [
            'advlist',
            'anchor',
            'autolink',
            'autoresize',
            //'autosave',
            //'bbcode',
            'charmap',
            'code',
            'colorpicker',
            //'compat3x',
            //'contextmenu',
            //'directionality',
            'emoticons',
            //'example',
            //'example_dependency',
            //'fullpage',
            'fullscreen',
            'hr',
            'image',
            'imagetools',
            //'insertdatetime',
            //'layer',
            //'legacyoutput',
            'link',
            'lists',
            //'importcss',
            'media',
            //'nonbreaking',
            //'noneditable',
            'pagebreak',
            'paste',
            'preview',
            'print',
            'save',
            'searchreplace',
            //'spellchecker',
            //'tabfocus',
            'table',
            //'template',
            'textcolor',
            'visualblocks',
            'visualchars',
            'wordcount'
        ]

        var default_values = {
            selector: 'textarea.mceEditor',
            theme : "modern",
            skin : 'lightgray',
            plugins : plugins.join(' '),
            menubar: false,
            statusbar: true,
            toolbar1: "code print preview fullscreen | removeformat visualchars visualblocks | undo redo | cut copy paste pastetext | searchreplace | image media link unlink anchor table bullist numlist hr emoticons charmap",
            toolbar2: "bold italic underline strikethrough superscript subscript | styleselect | formatselect | fontselect | fontsizeselect | forecolor backcolor | outdent indent | alignleft aligncenter alignright alignjustify",
            image_advtab: true,
            image_class_list : [
                { title: 'none', value: '' },
                { title: 'rounded', value: 'img-rounded' },
                { title: 'circle', value: 'img-circle' },
                { title: 'thumbnail', value: 'img-thumbnail' },
            ],
            pagebreak_separator : "<!-- page break -->",
            content_css : [
                site_url('static/css/custom.css'), 
                site_url('static/css/bootstrap.css'), 
                site_url('static/css/color.css')
            ],
            style_formats: [
                { title: 'Title green', block: 'h4', classes: 'title_green' }, 
                { title: 'Title orange', block: 'h4', classes: 'title_orange' }, 
                { title: 'Title blue', block: 'h4', classes: 'title_blue' },
                { title: 'Grow', selector: 'img', classes: 'grow' },
                { title: 'Grayscale', selector: 'img', classes: 'grayscale' }
            ],
            style_formats_autohide: true,
            table_appearance_options: false,
            table_class_list: [
                { title: 'none', value: '' },
                { title: 'table', value: 'table' },
                { title: 'table striped', value: 'table table-striped' },
                { title: 'table bordered', value: 'table table-bordered' },
                { title: 'table hover', value: 'table table-hover' },
                { title: 'table condensed', value: 'table table-condensed' }
            ],
            textcolor_map: [
                "227f78", "Title green",
                "faa627", "Title orange",
                "415060", "Title blue",
            ],
            convert_fonts_to_spans : true,
            fix_list_elements : true,
            force_hex_style_colors : true,
            file_browser_callback : _browser_callback,
            document_base_url : document_base_url,
            relative_urls : true,
            remove_script_host : true,
            entity_encoding : 'numeric'
        }

        if (params) {
            for (var key in params) {
                default_values[key] = params[key];
            }
        }

        tinyMCE.init(default_values);
    }

    /*************************************************************************
        Counter
    **************************************************************************/

    Bbpf.Counter = function(params) {
        this.target = Yeti.Element(params.target);
        if (this.target.firstChild === null) {
            this.target.appendChild(document.createTextNode('0'))
        }
        this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
    }

    Bbpf.Counter.prototype.get_value = function() {
        return parseInt(this.target.firstChild.data);
    }

    Bbpf.Counter.prototype.set_value = function(value) {
        var css_cls = value > 0 ? 'positive' : 'zero_or_neg';

        this.target.firstChild.data = value;
        Yeti.DOM.addClass(this.target, 'counter_' + css_cls);

        this.dispatcher.fire('after_counter_value_change', {
            value : value
        });
    }

    Bbpf.Counter.prototype.inc = function(value) {
        this.set_value(this.get_value() + (value ? value : 1));
    }

    Bbpf.Counter.prototype.dec = function(value) {
        this.set_value(this.get_value() - (value ? value : 1));
    }

    Bbpf.Counter.prototype.reset = function() {
        this.set_value(0);
    }

    Bbpf.Counter.prototype.checked = function(src) {
        src.checked ? this.inc() : this.dec();
    }


    /*************************************************************************
        Clipboard
    **************************************************************************/

    Bbpf.Clipboard = function(params) {
        this.container = Yeti.Element(params.container);
        this.cpt = new Bbpf.Counter({target: 'clipboard-counter'})
        this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        this.toggle_button = this.container.querySelector('button[data-toggle="dropdown"]');

        this.set_oids(params.oids);

        var self = this;
        
        Yeti.Element('clipboard-clear').addEventListener('click', function(e) {
            e.preventDefault();
            self.clear();
        });

        Yeti.Element('clipboard-paste').addEventListener('click', function(e) {
            e.preventDefault();
            self.dispatcher.fire('clipboard_paste', { evt: e } );
        });
    }

    Bbpf.Clipboard.prototype.set_oids = function(oids) {
        this.oids = oids;
        this.cpt.set_value(oids.length);

        if (oids.length == 0) {
            jQuery(this.toggle_button).addClass('disabled');
        } else {
            jQuery(this.toggle_button).removeClass('disabled');
        }
    }

    Bbpf.Clipboard.prototype.clear = function(params) {
        var self = this;

        Yeti.AjaxRequest(site_url('session/sremove'), {
            accept: 'json',
            method: 'POST',
            onreadystatechange : function(req) {
                if (req.success()) {
                    self.set_oids([]);
                    self.dispatcher.fire('clipboard_clear_success');
                } else if (req.error()) {
                    self.dispatcher.fire('clipboard_clear_error');
                }
            }
        });
    }   



    /*************************************************************************
        Calendar
    **************************************************************************/

    Bbpf.Calendar = function(params) {
        var _self = this;
        this.dmy = params.dmy || new Date(Date.now());
        this.container = Yeti.Element(params.container);
        this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        this.dispatcher.add('after_load_success', function() {
            this.add_nav_handlers(_self.container);
        });
    }

    Bbpf.Calendar.prototype.load = function(params) {
        var _self = this;
        Yeti.AjaxRequest(site_url('event/monthly_calendar'), {
            accept : 'xml',
            data : {
                month : _self.dmy.getMonth() + 1,
                year : _self.dmy.getFullYear()
            },
            onreadystatechange : function(req) {
                if (req.success()) {
                    var data = req.get_response(),
                        section_body = data.getElementsByTagName('body').item(0)
                    ; // var

                    if (section_body) {
                        Yeti.DOM.removeNodes(_self.container);
                        Yeti.DOM.appendClone(_self.container,
                            Yeti.DOM.importNode(
                                Yeti.DOM.firstElementChild(section_body),
                                true
                            )
                        );
                    }
                    _self.dispatcher.fire('after_load_success');
                } else if (req.error()) {
                    _self.dispatcher.fire('after_load_error');
                }
            }
        });
    }

    Bbpf.Calendar.prototype.next_month = function() {
        if (this.dmy.getMonth() > 10) {
            this.dmy = new Date(this.dmy.getFullYear() + 1, 0, 1);
        } else {
            this.dmy.setMonth(this.dmy.getMonth() + 1);
        }
        this.load();
    }

    Bbpf.Calendar.prototype.prev_month = function() {
        if (this.dmy.getMonth() == 0) {
            this.dmy = new Date(this.dmy.getFullYear() - 1, 11, 1);
        } else {
            this.dmy.setMonth(this.dmy.getMonth() - 1);
        }
        this.load();
    }

    Bbpf.Calendar.prototype.add_nav_handlers = function(src) {
        var src = src || document,
            links = src.getElementsByTagName('a'),
            _self = this
        ;

        for (var i=0, len=links.length; i<len; i++) {
            (function(el) {
                var direction = el.getAttribute('data-direction');
                if (direction) {
                    switch (direction) {
                        case 'previous':
                            el.addEventListener('click', function() {
                                _self.prev_month();
                            });
                            break;
                        case 'next':
                            el.addEventListener('click', function() {
                                _self.next_month();
                            });
                            break;
                    }
                }
            })(links[i]);
        }
    }


    /*************************************************************************
        Pagination
    **************************************************************************/

    Bbpf.Pagination = function(params) {
        this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        this._values = {
            limit: 10,
            offset: 0
        };

        if (params.values) {
            this.set_many(params.values);
        }
    }

    Bbpf.Pagination.prototype.set_many = function(obj) {
        for (var i in obj) {
            this.set(i, obj[i]);
        }
    }

    Bbpf.Pagination.prototype.set = function(key, value) {
        switch(key) {
            case 'offset':
            case 'limit':
            case 'count':
                var value = parseInt(value);

                if (value >= 0 && this.get(key) != value) {
                    this._values[key] = value;
                    this._values.page_current = this._values.offset / this._values.limit + 1;
                    this._values.page_total = Math.floor(this._values.count / this._values.limit);

                    if (this._values.count % this._values.limit != 0) {
                        this._values.page_total++;
                    }

                    this.dispatcher.fire(key + '_change', {
                        value: value
                    });
                }

                break;
        }
    }

    Bbpf.Pagination.prototype.get = function(key) {
        return this._values[key];
    }

    Bbpf.Pagination.prototype.first = function() {
        this.page(1);
    }

    Bbpf.Pagination.prototype.previous = function() {
        this.page(this.get('page_current') - 1);
    }

    Bbpf.Pagination.prototype.page = function(idx) {
        var idx = parseInt(idx);

        if (idx > this.get('page_total')) {
            idx = this.get('page_total');
        } else if (idx <= 0 || isNaN(idx)) {
            idx = 1;
        }

        this.set('offset', (idx - 1) * this.get('limit'));

        this.dispatcher.fire('pagination_change', {
            values: this._values
        });
    }

    Bbpf.Pagination.prototype.next = function() {
        this.page(this.get('page_current') + 1);
    }

    Bbpf.Pagination.prototype.last = function() {
        this.page(this.get('page_total'));
    }


    /*************************************************************************
        TagList
    **************************************************************************/

    Bbpf.TagList = function(params) {
        this.container = Yeti.Element(params.container);
    }

    Bbpf.TagList.prototype.load = function() {
        var _self = this;

        Yeti.AjaxRequest(this.url, {
            data: this.parameters,
            onreadystatechange: function(req) {
                if (req.success()) {
                    var data = JSON.parse(req.get_response());
                    Yeti.DOM.removeNodes(_self.container);
                    _self.build_select(data);
                    _self.dispatcher.fire('after_load_success');
                } else if (req.error()) {
                    _self.dispatcher.fire('after_load_error');
                }
            }
        });
    }

    Bbpf.TagList.prototype.build_select = function(data) {
        for (var i=0, _len = data.length; i<_len; i++) {
            var result = data[i];
            this.add_tag(result[0], result[1]);
        }
    }

    Bbpf.TagList.prototype.add_tag = function(tag, selected) {
        var opt = document.createElement('option');

        opt.setAttribute('value', tag.id);
        
        if (selected) {
            opt.setAttribute('selected', 'selected');
        }

        opt.appendChild(document.createTextNode(tag.name));

        this.container.appendChild(opt);

        return opt;
    }


    /*************************************************************************
        Tag
    **************************************************************************/

    Bbpf.Tag = function(params) {
        if (params) {
            for (var key in params) {
                this[key] = params[key];
            }
        }

        if (!this.dispatcher) {
            this.dispatcher = new Yeti.Tools.Dispatcher(this);
        }
    }

    Bbpf.Tag.prototype.save = function(params) {
        var _self = this;

        Yeti.AjaxRequest(site_url('tag'), {
            method : 'POST',
            accept : 'json',
            data : _self.data,
            onreadystatechange : function(req) {
                if (req.success()) {
                    var tag_json = JSON.parse(req.get_response());
                    _self.dispatcher.fire('after_save_success', {
                        tag: tag_json
                    });
                } else if (req.error()) {
                    _self.dispatcher.fire('after_save_error')
                }
            }
        });
    }


    /*************************************************************************
       ResponseParserComponent
    **************************************************************************/

    Bbpf.ResponseParserComponent = function(params) {
        this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        this.components = params.components;
    }

    Bbpf.ResponseParserComponent.prototype.parse_components = function(node) {
        /* node is the <components> */
        if (node.hasChildNodes()) {
            var children = node.childNodes,
                _self = this;

            for (var i=0, _len=children.length; i<_len; i++) {
                (function(elem) {
                    /* check if elem is an Element */
                    if (elem.nodeType == 1) {
                        var component = _self.components[elem.nodeName];
                        if (component) {
                            component.update_from_xml(elem);
                        }
                    }
                })(children[i]);
            }
        }
    }

    Bbpf.ResponseParserComponent.prototype.parse = function(xml_doc, level) {
        /* Start at the root (<response>) */
        var level = level == undefined ? 0 : level;

        for (var i=0, _len=xml_doc.childNodes.length; i<_len; i++) {
            var elem = xml_doc.childNodes[i];

            if (elem.nodeName == 'response' && level == 0) {
                /* Parse <response> */
                this.parse(elem, level+1);
            } else if (elem.nodeName == 'meta' && level == 1) {
                // TODO
            } else if (elem.nodeName == 'errors' && level == 2) {
                // TODO
            } else if (elem.nodeName == 'components' && level == 1) {
                /* Parse <response> -> <components> */
                this.parse_components(elem);
            } else {
                // nothing
            }
        }
    }


    /*************************************************************************
       Component
    **************************************************************************/

    Bbpf.Component = function(params) {
        if (params) {
            this.container = Yeti.Element(params.container);
            this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        }
    }

    Bbpf.Component.prototype.update_from_xml = function(node) {
        if (node.hasChildNodes()) {
            Yeti.DOM.removeNodes(this.container);
            for (var i=0, _len = node.childNodes.length; i<_len; i++) {
                Yeti.DOM.appendClone(
                    this.container,
                    Yeti.DOM.importNode(node.childNodes[i], true)
                );
            }
        }

        this.dispatcher.fire('after_update', {
            node: node
        });
    }


    /*************************************************************************
        NavigationComponent
    **************************************************************************/

    Bbpf.NavigationComponent = function(params) {
        if (params) {
            Bbpf.Component.call(this, params);
            this.dispatcher.add('after_update', function() {
                this.add_handlers();
            });
        }
    }

    Bbpf.NavigationComponent.prototype = new Bbpf.Component();
    Bbpf.NavigationComponent.prototype.constructor = Bbpf.NavigationComponent;

    Bbpf.NavigationComponent.prototype.add_handlers = function() {
        // TODO
    }


    /*************************************************************************
        PaginationComponent
    **************************************************************************/

    Bbpf.PaginationComponent = function(params) {
        if (params) {
            Bbpf.Component.call(this, params);
            this.pagination = params.pagination || new Bbpf.Pagination({});
            this.dispatcher.add('after_update', function() {
                this.add_handlers();
            });
        }
    }

    Bbpf.PaginationComponent.prototype = new Bbpf.Component();
    Bbpf.PaginationComponent.prototype.constructor = Bbpf.PaginationComponent;

    Bbpf.PaginationComponent.prototype.update_from_xml = function(node) {
        this.pagination.set('count', node.getAttribute('count'));
        this.pagination.set('offset', node.getAttribute('offset'));
        this.pagination.set('limit', node.getAttribute('limit'));

        Bbpf.Component.prototype.update_from_xml.call(this, node);
    }

    Bbpf.PaginationComponent.prototype.add_handlers = function() {
        var links = this.container.getElementsByTagName('a'),
            _self = this ;

        for (var i=0, _len=links.length; i<_len; i++) {
            (function(el) {
                var direction = el.getAttribute('data-direction');
                if (direction) {
                    el.addEventListener('click', function(e) {
                        e.preventDefault();

                        if (direction == 'goto') {
                            var page = el.getAttribute('data-page');
                            _self.pagination.page(page);
                        } else {
                            _self.pagination[direction]();
                        }
                    });
                }
            })(links[i]);
        }
    }


    /*************************************************************************
        FolderAdminComponent
    **************************************************************************/

    Bbpf.FolderAdminComponent = function(params) {
        Bbpf.Component.call(this, params);

        this.dispatcher.add('after_update', function() {
            this.add_action_handlers();
            this.add_action_handlers({
                selection: this.container.getElementsByTagName('input')
            });
        });
    }

    Bbpf.FolderAdminComponent.prototype = new Bbpf.Component();
    Bbpf.FolderAdminComponent.prototype.constructor = Bbpf.FolderAdminComponent;

    Bbpf.FolderAdminComponent.prototype._get_data = function(src) {
        /* This function returns the row container (tr) and the object data */
        var data = {};

        do {
            if (src.nodeType !== 1) {
                return data;
            }

            if (src.hasAttribute('data-obj')) {
                data.obj = JSON.parse(src.getAttribute('data-obj'));
            }

            if (src.tagName.toLowerCase() == 'tr') {
                data.container = src;
                return data;
            } else {
                src = src.parentNode;
            }

        } while (1)
    }

    Bbpf.FolderAdminComponent.prototype.toggle_select_objs = function(selection) {
        /* With a given selection of id (ex: [1,5,56,32,1541]) it selects or
         * deselects the corresponding object in the view */

        if (selection && selection.length > 0) {
            var inputs = this.container.getElementsByTagName('input'),
                cpt = 0
            ;

            for (var i=0, _ilen = inputs.length, _slen = selection.length; i<_ilen; i++) {
                /* For each <input> tag check that it has a
                 * data-purpose="select_object" attribute */
                var input = inputs[i];
                if (input.getAttribute('data-purpose') == 'select_object') {
                    var data = this._get_data(input);
                    if (data.obj && data.obj.id) {
                        for (var j=0; j<_slen; j++) {
                            if (selection[j] == data.obj.id) {
                                input.checked = !input.checked;
                                cpt ++;
                                this.dispatcher.fire('select_object', {
                                    obj: data.obj,
                                    container : data.container,
                                    src: input
                                });
                                break;
                            }
                        }
                    }
                }

                // small optimization
                if (cpt === _slen) {
                    break;
                }
            }
        }
    }

    // Handlers

    Bbpf.FolderAdminComponent.prototype.add_action_handlers = function(p) {
        /* This function add handlers on all p.selection tags which have a data-purpose
         * attribute. When clicked, the corresponding event is fired */

        p = p !== undefined ? p : {};

        var links = p.selection || this.container.getElementsByTagName('a'),
            _self = this
        ;

        for (var i=0, _len = links.length; i<_len; i++) {
            (function(el) {
                if (el.hasAttribute('data-purpose')) {
                    el.addEventListener(p.evt || 'click', function() {
                        var data = _self._get_data(el);

                        if (data) {
                            _self.dispatcher.fire(el.getAttribute('data-purpose'), {
                                obj: data.obj,
                                container: data.container,
                                src: el
                            });
                        }
                    });
                }
            })(links[i]);
        }
    }


    /*************************************************************************
        FolderController
    **************************************************************************/

    Bbpf.FolderSort = function(p) {
        this.key = p.key;
        this.direction = p.direction;
        this.nulls = p.nulls;
    }

    Bbpf.FolderController = function(params) {
        var _self = this;

        if (params) {
            this.url = params.url;
            this.folder = params.folder;
            this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
            this.parameters = params.parameters || {};
            this.components = params.components;
            this.selection = [];

            if (!this.parameters.filters) {
                this.parameters.filters = [];
            }

            this.response_parser = new Bbpf.ResponseParserComponent({
                components: params.components
            });

            this.dispatcher.add('change_weight_success', function() {
                delete(_self.selection_move);
                _self.refresh({});
            });

            this.dispatcher.add('after_delete_success', function() {
                _self.refresh({});
                _self.selection = [];
            });
        }
    }

    Bbpf.FolderController.prototype.add_selection = function(obj_id) {
        if (this.selection.indexOf(obj_id) === -1) {
            this.selection.push(obj_id);
        }
    }

    Bbpf.FolderController.prototype.remove_selection = function(obj_id) {
        var idx = this.selection.indexOf(obj_id);

        if (idx !== -1) {
            this.selection.splice(idx, 1);
        }
    }

    Bbpf.FolderController.prototype.clear_selection = function() {
        for (var i=0, _len = this.selection.length; i<_len; i++) {
            this.selection.pop();
        }
    }

    Bbpf.FolderController.prototype.add_sort = function(p) {
        if (!this.sort) {
            this.sort = [];
        }

        this.sort.push(p);
        this.refresh();
    }

    Bbpf.FolderController.prototype.add_filter = function(filter) {
        if (!this.has_filter(filter)) {
            this.parameters.filters.push(filter);
        }
    }

    Bbpf.FolderController.prototype.has_filter = function(filter) {
        return this.parameters.filters.indexOf(filter) !== -1;
    }

    Bbpf.FolderController.prototype.remove_filter = function(filter) {
        var idx = this.parameters.filters.indexOf(filter);

        if (idx !== -1) {
            this.parameters.filters.splice(idx, 1);
        }
    }

    Bbpf.FolderController.prototype.is_filtered = function() {
        return this.parameters.filters.length > 0;
    }

    /* Make the request to the server */
    Bbpf.FolderController.prototype.load = function() {
        var _self = this;

        this.dispatcher.fire('before_load');

        this.parameters.components = [];
        for (var i in this.components) {
            this.parameters.components.push(i);
        }

        if (this.sort) { 
            _self.parameters.sorts = [];
            this.sort.forEach(function(sort, cpt) {
                var s = '__s' + cpt;
                _self.parameters[s] = sort.key;
                _self.parameters[s + 'direction'] = sort.direction
                _self.parameters[s + 'nulls'] = sort.nulls
            });
        }
       
        Yeti.AjaxRequest(this.url, {
            data : this.parameters,
            accept : 'xml',
            onreadystatechange : function(req) {
                if (req.success()) {
                    _self.response_parser.parse(req.get_response());
                    _self.dispatcher.fire('after_load_success');
                } else if (req.error()) {
                    _self.dispatcher.fire('after_load_failure');
                }
            }
        });
    }

    Bbpf.FolderController.prototype.refresh = function(params) {
        for (var i in params) {
            this.parameters[i] = params[i];
        }

        this.load();
    }

    Bbpf.FolderController.prototype.move = function(params) {
        if (!this.selection_move) {
            this.selection_move = params;
            Yeti.DOM.addClass(params.container, 'info');
        } else if (this.selection_move == params.container) {
            delete(this.selection_move);
            Yeti.DOM.removeClass(params.container, 'info');
        } else {
            Yeti.DOM.addClass(params.container, 'success');
            Bbpf.Content.change_weight({
                from: this.selection_move,
                to: params,
                dispatcher: this.dispatcher
            });
        }
    }

    /* Handlers */

    Bbpf.FolderController.prototype.add_delete_selection_handler = function(src) {
        var elem = Yeti.Element(src),
            _self = this;

        elem.addEventListener('click', function() {
            Bbpf.Content.delete_objs(_self.selection, _self.dispatcher);
        });
    }

    Bbpf.FolderController.prototype.add_cut_selection_handler = function(src) {
        var elem = Yeti.Element(src),
            _self = this;

        elem.addEventListener('click', function() {
            Bbpf.Content.copy_objs(_self.selection, _self.dispatcher);
        });
    }

    Bbpf.FolderController.prototype.add_sort_handler = function(src) {
         var src = Yeti.Element(src) || document,
             links = src.getElementsByTagName('a'),
             _self = this;

         for (var i=0, _len=links.length; i<_len; i++) {
             (function(el) {
                 var sort = el.getAttribute('data-sort');
                 if (sort) {
                     el.addEventListener('click', function() {

                        if (_self.parameters.__s0 == sort) {
                            if (_self.parameters.__s0direction == 'asc') {
                                _self.parameters.__s0direction = 'desc';
                            } else {
                                _self.parameters.__s0direction = 'asc';
                            }
                        } else {
                            _self.parameters.__s0direction = 'asc';
                        }

                         _self.refresh({
                            __s0 : sort
                         });
                         _self.dispatcher.fire('after_sort_clicked', {
                             src : el
                         });
                     });
                 }
             })(links[i]);
         }
    }

    /*************************************************************************
        Content
    **************************************************************************/

    Bbpf.Content = function(params) {
        if (params) {
            this.load(params);
            this.dispatcher = params.dispatcher || new Yeti.Tools.Dispatcher(this);
        }
    }


    /* Initialize an object */
    Bbpf.Content.prototype.load = function(params) {
        for (var key in params) {
            this[key] = params[key];
        }
    }

    /* Utility functions ("static-like" methods) */

    Bbpf.Content.delete_objs = function(selection, dispatcher) {
        if (selection.length > 0 && confirm('Are you sure?')) {
            Yeti.AjaxRequest(site_url('entities/delete'), {
                method : 'POST',
                accept : 'json',
                data : {
                    oid : selection
                },
                onreadystatechange : function(req) {
                    if (req.success()) {
                        var json = JSON.parse(req.get_response());
                        dispatcher.fire('after_delete_success', {
                            data : json
                        });
                    } else if (req.error()) {
                        dispatcher.fire('after_delete_error');
                    }
                }
            });
        }
    }

    Bbpf.Content.copy_objs = function(selection, dispatcher) {
        if (selection.length > 0 ) {
            Yeti.AjaxRequest(site_url('session/scopy'), {
                method : 'POST',
                accept : 'json',
                data : {
                    oid : selection
                },
                onreadystatechange : function(req) {
                    if (req.success()) {
                        var json = JSON.parse(req.get_response());
                        dispatcher.fire('after_copy_success', {
                            data : json
                        });
                    } else if (req.error()) {
                        dispatcher.fire('after_copy_error');
                    }
                }
            });
        }
    }

    Bbpf.Content.change_weight = function(p) {
        Yeti.AjaxRequest(site_url(p.from.obj.id + '/weight'), {
            accept: 'json',
            method: 'POST',
            data : {
                content_id: p.from.obj.id,
                weight: p.to.obj.weight
            },
            onreadystatechange : function(req) {
                if (req.success()) {
                    p.dispatcher.fire('change_weight_success');
                } else if (req.error()) {
                    p.dispatcher.fire('change_weight_error', {
                        from: p.from,
                        to: p.to
                    });
                }
            }
        });
    }


    /*************************************************************************
        Folder
    **************************************************************************/

    Bbpf.Folder = function(params) {
        Bbpf.Content.call(this, params)
    }
    Bbpf.Folder.prototype = new Bbpf.Content();
    Bbpf.Folder.prototype.constructor = Bbpf.Folder;


    Bbpf.Folder.prototype.paste = function(params) {
        if (confirm('Are you sure that you want to move those items ? They will me moved from their original location !')) {
            var _self = this;
            Yeti.AjaxRequest(site_url(this.id, 'paste'), {
                method: 'POST',
                onreadystatechange : function(req) {
                    if (req.success()) {
                        _self.dispatcher.fire('after_paste_success');
                    }
                }
            });
        }
    }

    /*************************************************************************
        Document
    **************************************************************************/

    Bbpf.Document = function(params) {
        Bbpf.Content.call(this, params);
    }
    Bbpf.Document.prototype = new Bbpf.Content();
    Bbpf.Document.prototype.constructor = Bbpf.Document;

    /*************************************************************************
        Event
    **************************************************************************/

    Bbpf.Event = function(params) {
        Bbpf.Content.call(this, params);
    }

    Bbpf.Event.prototype = new Bbpf.Content();
    Bbpf.Event.prototype.constructor = Bbpf.Event;

    Bbpf.Event.prototype.is_georeferenced = function() {
        return this.address_latitude && this.address_longitude;
    }

    Bbpf.Event.prototype.GeocodingHandler = function(src_form, map) {
        var form = src_form;

        if (this.is_georeferenced()) {
            var point = new google.maps.LatLng(this.address_latitude, 
                                               this.address_longitude);
        } else {
            var point = new google.maps.LatLng(50, 0);
        }

        var map = new google.maps.Map(Yeti.Element(map), {
            zoom : 10,
            center : point,
            zoom : this.address ? 10 : 4,
            mapTypeId : google.maps.MapTypeId.ROADMAP
        });

        // The global marker which indicates the address
        var marker = new google.maps.Marker({
            position : point,
            draggable : true,
            map : map
        });

        // When we move the marker, update the two hidden fields (latitude and
        // longitude)
        google.maps.event.addListener(marker, "dragend", function() {
            var coords = marker.getPosition();
            form.address_latitude.value = coords.lat();
            form.address_longitude.value = coords.lng();
        });

        // Test if the event has already a georeferenced address. If
        // yes, add the marker.
        marker.setVisible(this.is_georeferenced());

        var geocoder = new google.maps.Geocoder();
        form.country_iso.onchange = form.address.onblur = function(evt) {
            // " foo     bar     " => "foo bar"
            var q = form.address.value.replace(/(?:^\s+)|(?:\s+$)/g, '').replace(/\s{2,}/g, ' ');
            var zoom = 10;

            if (q.length > 0) {
                if (q.charAt(q.length - 1) != ',') {
                    q = q.concat(', ');
                }
            } else {
                zoom = 4;
            }

            // Concat the address with the selected country name
            q = q.concat(form.country_iso.options[form.country_iso.selectedIndex].text);

            // Now q contains "address, country". If we can find this
            // address, then 1) add its latitude/longitude to the two
            // hidden fields 2) zoom to this address 3) add a marker. If
            // we can't find the address, then set latitude/longitude to
            // null.

            geocoder.geocode({'address' : q}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var point = results[0].geometry.location;
                    marker.setPosition(point);
                    form.address_latitude.value = point.lat();
                    form.address_longitude.value = point.lng();
                    map.setCenter(point);
                    map.setZoom(zoom);
                    marker.setVisible(true);
                } else {
                    marker.setVisible(false);
                    form.address_latitude.value = form.address_longitude.value = null;
                }
            });

        }
    }
})(window);
