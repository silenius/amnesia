import * as bbpf from "../../../bbpf";

document.addEventListener("DOMContentLoaded",function(e) {
    const data = document.getElementById('main'),
        folder_data = data.getAttribute('data-folder'),
        url = data.getAttribute('data-folder-url'),
        folder = new bbpf.Folder(folder_data),
        pagination = new bbpf.Pagination({}),
        folder_browser = new bbpf.FolderController({
            url : url,
            folder : folder_data,
            components : {
                main : new bbpf.Component({
                    container : 'content'
                }),
                pagination : new bbpf.PaginationComponent({
                    container : 'pagination',
                    pagination : pagination
                })
            },
            parameters : {
                display : "list",
                limit : pagination.get('limit')
            }
        });

    pagination.dispatcher.add('pagination_change', function() {
        folder_browser.refresh({
            limit: this.get('limit'),
            offset: this.get('offset')
        });
    });

    folder_browser.dispatcher.add('before_load', function() {
        var content_icon = Yeti.Element('content_icon');
        if (content_icon) {
            if (this.parameters.display == 'list') {
                content_icon.style.display = 'inline';
            } else {
                content_icon.style.display = 'none';
            }
        }
    });

    folder_browser.load();
});
