;(function(ns) {

    var UI = ns.UI = new Object();

    /***********************************************************************
        Frame
    ************************************************************************/

    UI.Frame = function(params) {
        var _self = this;

        /* Default options */
        this.options = {
            zindex : 1000,
            position : 'center',
            onscroll : 'scroll',
            overlay : true,
            title : '',
            body : null,
            width : 300,
            height : 300
        }
        this.update_options(params);

        if (this.options.onscroll == 'scroll') {
            Yeti.Evt.bind(window, 'scroll', function() {
                _self.set_sizes();
                _self.set_position();
            });
        }

        this.container = document.body;
        this.frame = document.createElement('div');
        this.header = document.createElement('div');
        this.title = document.createElement('span');

        if (this.options.body === null) {
            this.body = document.createElement('div');
        } else {
            this.body = Yeti.Element(this.options.body);
        }

        this.frame.style.zIndex = this.options.zindex;
        this.frame.style.position = 'absolute';

        if (this.options.overlay) {
            var window_size = Yeti.DOM.getWindowSize();

            this.overlay = document.createElement('div')
            this.overlay.style.top = 0 + 'px';
            this.overlay.style.left = 0 + 'px';
            this.overlay.style.position = 'absolute';
            this.overlay.style.zIndex = this.frame.zIndex - 1;
            Yeti.DOM.addClass(this.overlay, 'ui-frame-overlay');

            this.overlay.style.width = Math.max(window_size.width,
                document.body.scrollWidth) + 'px';

            this.overlay.style.height = Math.max(window_size.height,
                document.body.scrollHeight) + 'px';

            Yeti.Evt.bind(this.overlay, 'click', function() {
                _self.detach();
            });
        } else {
            this.overlay = undefined;
        }

        Yeti.DOM.addClass(this.frame, 'ui-frame');
        Yeti.DOM.addClass(this.header, 'ui-frame-header');
        Yeti.DOM.addClass(this.title, 'ui-frame-title');
        Yeti.DOM.addClass(this.body, 'ui-frame-body');

        this.header.appendChild(this.title);
        this.frame.appendChild(this.header);
        this.frame.appendChild(this.body);

        this.set_title(this.options.title);

        this.set_sizes();
        this.set_position();
    }

    UI.Frame.prototype.update_options = function(opts) {
        for (var i in opts) {
            this.options[i] = opts[i];
        }
    }

    UI.Frame.prototype.get_frame_size = function() {
        var size = new Object(),
            props = ['width', 'height']
        ;

        for (var i=0, _len = props.length; i<_len; i++) {
            var key = props[i],
                value = this.options[key]
            ;

            switch(typeof(value)) {
                case 'number':
                    size[key] = value;
                    break;
                case 'string':
                    var idx_percent = value.lastIndexOf('%');
                    if (idx_percent == -1) {
                        size[key] = parseInt(value);
                    } else {
                        var window_size = Yeti.DOM.getWindowSize();
                        size[key] = window_size[key] * (parseInt(value.substring(0, idx_percent)) / 100);
                    }
                    break;
            }
        }

        return size;
    }

    UI.Frame.prototype.set_sizes = function() {
        var size = this.get_frame_size();

        this.frame.style.width = size.width + 'px';
        this.frame.style.height = size.height + 'px';
        this.body.style.height = (size.height - this.header.offsetHeight) -20 + 'px';
    }

    UI.Frame.prototype.get_position = function() {
        var window_size = Yeti.DOM.getWindowSize(),
            scroll_offset = Yeti.DOM.getScrollXY()
        ;

        if (this.options.position == 'center') {
            var left = window_size.width / 2 + scroll_offset.X,
                top = window_size.height / 2 + scroll_offset.Y,
                frame_size = this.get_frame_size()
            ;

            /* Additional border/padding/... ? */
            if (this.frame.clientLeft) {
                left -= this.frame.clientLeft;
                top -= this.frame.clientTop;
            }

            return {
                left : left - frame_size.width / 2,
                top : top - frame_size.height / 2
            }
        }
    }

    UI.Frame.prototype.set_position = function() {
        var position = this.get_position();

        this.frame.style.left = position.left + 'px';
        this.frame.style.top = position.top + 'px';
    }

    UI.Frame.prototype.set_title = function(value) {
        Yeti.DOM.removeNodes(this.title);
        this.title.appendChild(document.createTextNode(value));
    }

    UI.Frame.prototype.attach = function() {
        if (this.overlay) {
            this.container.appendChild(this.overlay);
        }
        this.container.appendChild(this.frame);
        this.body.style.display = 'block';
        this.attached = true;
    }

    UI.Frame.prototype.detach = function() {
        if (this.overlay) {
            this.container.removeChild(this.overlay);
        }
        this.container.removeChild(this.frame);
        this.attached = false;
    }

    UI.Frame.prototype.toggle = function() {
        this.attached ? this.detach() : this.attach();
    }

})(Yeti);
