/*
 *  This is:
 *   __  __________________
 *   \ \/ / ____/_  __/  _/
 *    \  / __/   / /  / /
 *    / / /___  / / _/ /
 *   /_/_____/ /_/ /___/
 *
 *  a simple Javascript library \o/
 *
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <julien.cigar@gmail.com> wrote this file. As long as you retain this notice
 * you can do whatever you want with this stuff. If we meet some day, and you
 * think this stuff is worth it, you can buy me a beer in return.
 * ----------------------------------------------------------------------------
 */

;(function(ns) {

    var Yeti = ns.Yeti = {};

    /* Simple URL cleaner */

    Yeti.url_for = function() {
        return Array.prototype.slice.call(arguments).join('/').replace(/\/{2,}/, '/');
    }

    /* Wrapper for document.getElementById */

    Yeti.Element = function(src) {
        return typeof(src) === 'string' ? document.getElementById(src) : src;
    }


    /***********************************************************************
        Global Javascript objects

        Workarounds for browsers which do not natively support some ECMA
        standards.

        Although extending the DOM is a very bad idea and considered "evil",
        adding missing methods to global javascript objects is perfectly
        acceptable.
    ************************************************************************/

    /* Array.indexOf
     * Returns the first (least) index of an element within the array equal
     * to the specified value, or -1 if none is found.
     *
     * Implementation is taken from https://developer.mozilla.org and is
     * exactly the one specified in ECMA-262.
     */

    if (!Array.prototype.indexOf) {  
        Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
            "use strict";

            if (this == null) {
                throw new TypeError();
            }

            var t = Object(this);
            var len = t.length >>> 0;

            if (len === 0) {
                return -1;
            }

            var n = 0;

            if (arguments.length > 0) {
                n = Number(arguments[1]);
                if (n != n) { // shortcut for verifying if it's NaN
                    n = 0;
                } else if (n != 0 && n != Infinity && n != -Infinity) {
                    n = (n > 0 || -1) * Math.floor(Math.abs(n));
                }
            }

            if (n >= len) {
                return -1;
            }

            var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);

            for (; k < len; k++) {
                if (k in t && t[k] === searchElement) {
                    return k;
                }
            }

            return -1;
        }
    }

    /* Array.lastIndexOf
     * Returns the last (greatest) index of an element within the array equal
     * to the specified value, or -1 if none is found.
     *
     * Implementation is taken from https://developer.mozilla.org and is
     * exactly the one specified in ECMA-262.
     */

    if (!Array.prototype.lastIndexOf) {
        Array.prototype.lastIndexOf = function(searchElement /*, fromIndex*/) {
        "use strict";

        if (this == null) {
            throw new TypeError();
        }

        var t = Object(this);
        var len = t.length >>> 0;

        if (len === 0) {
            return -1;
        }

        var n = len;

        if (arguments.length > 1) {
            n = Number(arguments[1]);
            if (n != n) {
                n = 0;
            } else if (n != 0 && n != (1 / 0) && n != -(1 / 0)) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }

        var k = n >= 0 ? Math.min(n, len - 1) : len - Math.abs(n);

        for (; k >= 0; k--) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }

        return -1;
      };
    }

    /* Array.forEach
     * Executes a provided function once per array element.
     */

    if (!Array.prototype.forEach) {
        Array.prototype.forEach = function(callable, scope) {
            for(var i=0, _len = this.length; i < _len; ++i) {
                callable.call(scope, this[i], i, this);
            }
        }
    }

    /* String.trim
     * Removes whitespace from both ends of the string.
     */

    if (!String.prototype.trim) {  
        String.prototype.trim = function () {  
            return this.replace(/^\s+|\s+$/g, '');  
        };
    }


    /***********************************************************************
        Str
    ************************************************************************/

    Yeti.Str = {};

    /* Yeti.Str.reverse
     * Returns the string reversed.
     */

    Yeti.Str.reverse = function(src) {
        return src.split('').reverse().join('');
    }


    /***********************************************************************
        XMLHttpRequest
    ************************************************************************/

    Yeti.XMLHttpRequest = function() {
        if (window.XMLHttpRequest) {
            return new window.XMLHttpRequest();
        } else if (window.ActiveXObject) {
            return new window.ActiveXObject('Microsoft.XMLHTTP');
        } else {
            return null;
        }
    }


    /***********************************************************************
        AjaxRequest
    ************************************************************************/

    Yeti.AjaxRequest = function(url, opts) {
        var req = Yeti.XMLHttpRequest(),
            /* Request headers */
            headers = {
                'x-requested-with' : 'XMLHttpRequest'
            },

            /* Accept mapping */
            accepts = {
                json : 'application/json, text/json, text/javascript',
                html : 'text/html',
                xml : 'application/xml, text/xml',
                text : 'text/plain'
            },

            /* Default options */
            options = {
                method : 'GET',
                async : true,
                content_type : 'application/x-www-form-urlencoded',
                charset : 'UTF-8',
                data : null,
                cache : true,
                accept : undefined,
                headers : {},
                response_factory : Yeti.AjaxResponse
            }
        ; // var

        /* Override default options */
        for (var i in opts || {}) {
            options[i] = opts[i];
        }

        options.method = options.method.toUpperCase();

        if (options.method === 'POST') {
            headers['Content-Type'] = options.content_type +
                (options.charset ? '; charset=' + options.charset : '');
        }

        /* Serialize parameters to a query string and append it to the URL if
         * method is GET
         */
        if (options.data && typeof(options.data) !== 'string') {
            options.data = new Yeti.Tools.Serializer(options.data).toString();
            if (options.method === 'GET') {
                url += (url.indexOf('?') === -1 ? '?' : '&') + options.data;
            }
        }

        /* Append a timestamp to the url to avoid caching */
        if (!options.cache) {
            var __ts = '__ts=' + (new Date()).getTime();

            if (url.indexOf('__ts=') === -1) {
                url += (url.indexOf('?') === -1 ? '?' : '&') + __ts;
            } else {
                url = url.replace(/(:?__ts=\d+)/, __ts);
            }
        }

        req.onreadystatechange = function() {
            return options.onreadystatechange(new options.response_factory(this));
        }

        req.open(options.method, url, options.async)

        /* User-defined headers */
        for (var i in options.headers) {
            headers[i.toLowerCase()] = options.headers[i];
        }

        /* Ensure that the "Accept" header is properly set */
        if (!headers.accept) {
            headers.accept = accepts[options.accept] !== undefined ?
                             accepts[options.accept] : '*/*';
        }

        /* Set request headers */
        for (var i in headers) {
            req.setRequestHeader(i, headers[i]);
        }

        req.send(options.data)
    }


    /***********************************************************************
        AjaxResponse
    ************************************************************************/

    Yeti.AjaxResponse = function(req) {
        this.o = req;
        this.readyStates = ['uninitialized', 'loading', 'loaded',
                            'interactive', 'complete'];
    }

    Yeti.AjaxResponse.prototype.get_status = function() {
        var code = this.o.status;

        if ((code >= 200 && code < 300) || code == 304) {
            return 'ok';
        } else if (code >= 400 && code < 600) {
            return 'fail';
        } else {
            return 'unknown';
        }
    }

    Yeti.AjaxResponse.prototype.get_state = function() {
        return this.readyStates[this.o.readyState] || 'unknown';
    }

    Yeti.AjaxResponse.prototype.get_response = function() {
        if (this.o.responseXML) {
            return this.o.responseXML;
        } else {
            return this.o.responseText
        }
    }

    Yeti.AjaxResponse.prototype.success = function() {
        return this.get_state() == 'complete' && this.get_status() == 'ok';
    }

    Yeti.AjaxResponse.prototype.error = function() {
        return this.get_state() == 'complete' && this.get_status() == 'fail';
    }


    /***********************************************************************
        JSON
    ************************************************************************/

    Yeti.JSON = {};

    /* Yeti.JSON.parse
     * Parses a string as JSON and returns the parsed value.
     */

    Yeti.JSON.parse = function(data) {
        return typeof(JSON) !== 'undefined' ?
        JSON.parse(data) :
        (function(src) {
            // Taken from RFC 4627 (http://tools.ietf.org/html/rfc4627)
            var json = !(/[^,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]/.test(src.replace(/"(\\.|[^"\\])*"/g, '')));
            return json ? eval('(' + json + ')') : null;
        })(data);
    }


    /***********************************************************************
        Event
    ************************************************************************/

    Yeti.Evt = {};

    /* Yeti.Evt.preventDefault
     * Cancels the event if it is cancelable, without stopping further 
     * propagation of the event.
     */

    Yeti.Evt.preventDefault = function(e) {
        e.preventDefault ? e.preventDefault()
                         : e.returnValue = false;
    }

    /* Yeti.Evt.bind
     * Wrapper for .addEventListener and .attachEvent.
     */

    Yeti.Evt.bind = function(obj, type, listener, capture) {
        if ((type.substr(0,2).toLowerCase()) == 'on') {
            type = type.substr(2);
        }

        if (typeof(capture) != 'boolean') {
            capture = false;
        }

        if (obj.addEventListener) {
            obj.addEventListener(type, listener, capture);
        } else if (obj.attachEvent) {
            obj['__e' + type + listener] = listener;

            obj[type + listener] = function() { 
                obj['__e' + type + listener](window.event); 
            }

            obj.attachEvent('on' + type, obj[type + listener] );
        } else {
            ;
        }
    }

    /* Yeti.Evt.unbind
     * Wrapper for .removeEventListener and .detachEvent.
     */

    Yeti.Evt.unbind = function(obj, type, listener, capture) {
        if ((type.substr(0,2).toLowerCase()) == 'on') {
            type = type.substr(2);
        }

        if (typeof(capture) != 'boolean') {
            capture = false;
        }

        if (obj.removeEventListener) {
            obj.removeEventListener(type, listener, capture);
        } else if (obj.detachEvent) {
            obj.detachEvent('on' + type, obj[type + listener]);

            // Prevent a memory leak in IE.
            try {
                // Check if delete is supported
                delete(obj[type + listener]);
                delete(obj['__e' + type + listener]);
            } catch(e) {
                obj[type + listener] = null;
                obj['__e' + type + listener] = null;
            }
        } else {
            ;
        }
    }

    /***********************************************************************
        DOM
    ************************************************************************/

    Yeti.DOM = {};

    /* Yeti.DOM.importNode
     * Creates a copy of a node from an external document that can be
     * inserted into the current document.
     */

    Yeti.DOM.importNode = function(node, deep) {
        if (deep === undefined) {
            deep = true;
        }

        /* Note: document.importNode exists in IE9 but fails. Just fails. It's
         * not implemented, just says it's there and fails when called.
         */
        try {
            return document.importNode(node, deep);
        } catch(e) {
            return (function(node, deep) {
                /* Returns an integer code representing the type of the node. */
                var NodeTypes = {
                    ELEMENT_NODE : 1,
                    ATTRIBUTE_NODE : 2,
                    TEXT_NODE : 3,
                    CDATA_SECTION_NODE : 4,
                    ENTITY_REFERENCE_NODE : 5,
                    ENTITY_NODE : 6,
                    PROCESSING_INSTRUCTION_NODE : 7,
                    COMMENT_NODE : 8,
                    DOCUMENT_NODE : 9,
                    DOCUMENT_TYPE_NODE : 10,
                    DOCUMENT_FRAGMENT_NODE : 11,
                    NOTATION_NODE : 12
                }

                switch (node.nodeType) {
                    case NodeTypes.ELEMENT_NODE:
                        var newNode = document.createElement(node.nodeName);

                        if (node.attributes && node.attributes.length > 0) {
                            for (var i=0, _len=node.attributes.length ; i<_len ; i++) {
                                var attr_name = node.attributes[i].nodeName,
                                    attr_value = node.getAttribute(attr_name)
                                ;

                                if (attr_name.toLowerCase() == 'style') {
                                    newNode.style.cssText = attr_value;
                                } else if (attr_name.toLowerCase() == 'class') {
                                    newNode.className = attr_value;
                                } else if (attr_name.slice(0,2) == 'on') {
                                    // FIXME: slow...
                                    newNode[attr_name] = new Function(attr_value);
                                } else {
                                    newNode.setAttribute(attr_name, attr_value);
                                }
                            }
                        }

                        if (deep && node.hasChildNodes()) {
                            for (var i=0, _len=node.childNodes.length ; i<_len ; i++) {
                                newNode.appendChild(Yeti.DOM.importNode(node.childNodes[i], deep));
                            }
                        }

                        return newNode;
                        break;

                    case NodeTypes.TEXT_NODE:
                        return document.createTextNode(node.nodeValue);
                        break;

                    case NodeTypes.CDATA_SECTION_NODE:
                        return document.createCDATASection(node.nodeValue);
                        break;

                    case NodeTypes.COMMENT_NODE:
                        return document.createComment(node.nodeValue);
                        break;

                }
            })(node, deep);
        }
    }

    /* Yeti.DOM.firstElementChild
     * Returns a reference to the first child node of that element which is of
     * nodeType 1.
     */

    Yeti.DOM.firstElementChild = function(elem) {
        return elem.firstElementChild ?
        elem.firstElementChild :
        (function(elem) {
            for (var i=0, _len=elem.childNodes.length; i<_len; i++) {
                if (elem.childNodes[i].nodeType === 1) {
                    return elem.childNodes[i];
                }
            }
            return null;
        })(elem);
    }

    /* Yeti.DOM.getElementsByClassName
     * Returns a set of elements which have all the given class names.
     */

    Yeti.DOM.getElementsByClassName = function(name, src) {
        var src = src || document;

        return src.getElementsByClassName ?
        src.getElementsByClassName(name) :
        (function(name, src) {
            var class_pattern = new RegExp("(?:^|\\s)" + name + "(?:\\s|$)"),
                elems = [],
                selection = src.getElementsByTagName('*')
            ;

            for (var i=0, _len=selection.length; i<_len; i++) {
                if (class_pattern.test(selection[i].className)) {
                    elems.push(selection[i]);
                }
            }

            return elems;
        })(name, src);
    }

    /* Yeti.DOM.firstElementTag
     * Returns a reference to the first child node of that element which is of
     * nodeType 1 and of tag <tag>.
     */
    Yeti.DOM.firstElementTag = function(elem, tag) {
        var tag = tag.toUpperCase();
        for (var i=0, _len=elem.childNodes.length; i<_len; i++) {
            var child = elem.childNodes[i];
            if (child.nodeType === 1 && child.nodeName.toUpperCase() == tag) {
                return child;
            }
        }
        return null;
    }

    /* Yeti.DOM.removeNodes
     * Removes all child nodes from an element.
     */

    Yeti.DOM.removeNodes = function(elem) {
        var removed = 0;

        while(elem.hasChildNodes()) {
            elem.removeChild(elem.lastChild);
            removed++;
        }

        return removed;
    }

    /* Yeti.DOM.appendClone
     * Append a cloned node to an element. Needed because elem.appendChild()
     * on an imported node (document.importNode) is broken under IE
     */

    Yeti.DOM.appendClone = function(node, cloned_node) {
        document.importNode
            ? node.appendChild(cloned_node)
            : node.appendChild(cloned_node).innerHTML = cloned_node.innerHTML;
    }

    /* Yeti.DOM.addClass
     * Append a class to an element.
     */

    Yeti.DOM.addClass = function(elem, value) {
        var values = value.split(/\s+/);

        if (elem.className) {
            values = values.concat(elem.className.split(/\s+/)).sort();
            var i = 0,
                _len = values.length
            ;

            while (i < _len) {
                while(values[i] === values[i+1]) {
                    values.splice(i, 1);
                    _len--;
                }
                i++;
            }
        }

        elem.className = values.join(' ');
    }

    /* Yeti.DOM.removeClass
     * Remove a class from an element.
     */

    Yeti.DOM.removeClass = function(elem, value) {
        if (elem.className) {
            var values = value.split(' '),
                new_cls = elem.className
            ;

            for (var i=0, _len=values.length; i<_len; i++) {
                new_cls = new_cls.replace(values[i], ' ');
            }

            elem.className = new_cls.replace(/\s{2,}/g, ' ').trim();

            if (elem.className.length == 0) {
                elem.removeAttribute('class');
            }
        }
    }

    /* Yeti.DOM.getWindowSize
     * Returns the size of the browser window.
     */

    Yeti.DOM.getWindowSize = function() {
        return typeof(window.innerHeight) == 'number' ? {
            height : window.innerHeight,
            width : window.innerWidth
        } : document.body && document.body.clientHeight ? {
                height : document.body.clientHeight,
                width : document.body.clientWidth
            } : document.documentElement &&
                document.documentElement.clientHeight ? {
                    height : document.documentElement.clientHeight,
                    width : document.documentElement.clientWidth
                } : undefined
    }

    /* Yeti.DOM.getScrollXY
     * Returns the number of pixels that the document has already been 
     * scrolled.
     */

    Yeti.DOM.getScrollXY = function() {
        return typeof(window.pageYOffset) == 'number' ? {
            Y : window.pageYOffset,
            X : window.pageXOffset
        } : document.body && document.body.scrollLeft ? {
                Y : document.body.scrollTop,
                X : document.body.scrollLeft
            } : document.documentElement &&
                document.documentElement.scollLeft ? {
                    Y : document.documentElement.scrollTop,
                    X : document.documentElement.scrollLeft
                } : { Y : 0, X : 0 }
    }


    /***********************************************************************
        Tools
    ************************************************************************/

    Yeti.Tools = {};

    /* Yeti.Tools.typeOf
     * Returns a detailed text of the constructor
     */

    Yeti.Tools.typeOf = function(obj) {
        return Object().toString.call(obj).match(/(\w+)/ig)[1];
    }

    /* Yeti.Tools.Serializer
     * Serialize an object.
     */

    Yeti.Tools.Serializer = function(obj) {
        this.qs = [];

        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                this._encodeValue(key, obj[key]);
            }
        }
    }

    Yeti.Tools.Serializer.prototype.toString = function() {
        return this.qs.join('&');
    }

    Yeti.Tools.Serializer.prototype._encodeValue = function(key, value) {
        switch (value) {
            case null:
            case undefined:
                this._encodeString(key, value);
                break;
            default:
                switch (value.constructor) {
                    case Array:
                        this._encodeArray(key, value);
                        break;
                    default:
                        this._encodeString(key, value);
                        break;
                }
                break;
        }
    }

    Yeti.Tools.Serializer.prototype._encodeArray = function(key, value) {
        for (var i=0, _len=value.length ; i<_len ; i++) {
            this._encodeValue(key, value[i]);
        }
    }

    Yeti.Tools.Serializer.prototype._encodeString = function(key, value) {
        this.qs.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
    }

    /* Yeti.Tools.Dispatcher
     * A simple subscribe/publish dispatcher
     */ 
 
    Yeti.Tools.Dispatcher = function(scope) {
        this.default_scope = scope || this;
        this.callbacks = {};
    }

    Yeti.Tools.Dispatcher.prototype.add = function(evt, callback, scope) {
        if (!this.callbacks[evt]) {
            this.callbacks[evt] = [];
        }

        this.callbacks[evt].push({
            'callback' : callback,
            'scope' : scope || this.default_scope
        });
    }

    Yeti.Tools.Dispatcher.prototype.remove = function(evt) {
        if (this.callbacks[evt]) {
            delete this.callbacks[evt];
        }
    }

    Yeti.Tools.Dispatcher.prototype.fire = function(evt, params) {
        var cbs = this.callbacks[evt];

        if (!cbs) {
            return false;
        }

        for (var i=0, _len=cbs.length; i<_len; i++) {
            cbs[i].callback.call(cbs[i].scope, params, arguments);
        }
    }

})(window);
