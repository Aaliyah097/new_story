on_load();

function get_current_topic(){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    let slug = window.location.href.split('/')[window.location.href.split('/').length - 2];
    let data;
    $.ajax(
         {
             type: 'get',
             url: '/get-current-topic/' + slug + '/',
             headers: {'X-CSRFToken': csrf_token},
             mode: 'same-origin',
             async: false,
             success : function(json)
             {
               data = json;
             },
             error : function(xhr,errmsg,err) {
                alert('Ошибка!', 'Повторите попытку позднее.');
             }
         }
     )
    return data;
}

function get_more_tree_data(){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    let data;
    let slug = window.location.href.split('/')[window.location.href.split('/').length - 2];
    $.ajax(
         {
             type: 'get',
             url: '/more-tree/' + slug + '/',
             headers: {'X-CSRFToken': csrf_token},
             mode: 'same-origin',
             async: false,
             success : function(json)
             {
               data = json;
             },
             error : function(xhr,errmsg,err) {
                alert('Ошибка!', 'Повторите попытку позднее.');
             }
         }
     )
    return data[0];
}

async function plot_more_tree(data){
    $('#more_tree').jstree({
        'core': {
            'data': data
        }
    });
}

async function on_load(){
    await plot_more_tree(get_more_tree_data());
}

document.addEventListener("DOMContentLoaded", function(event) {
    //plot_more_tree(get_more_tree_data());

    let topic = get_current_topic()

    $('#more_tree')
        // listen for event
        .on('changed.jstree', function (e, data) {
            var i, j, r = [];
            let node = 0;
            for(i = 0, j = data.selected.length; i < j; i++) {
                node = data.instance.get_node(data.selected[i]).data;
            }
            window.location.href = '/topic/' + node;
        }).on('ready.jstree', function (e, data) {
            var node = $('#more_tree').jstree('get_node', String(topic.id), as_dom=true).find('a:first');;
            node.css("background-color", "#00CC4F");
            node.css("color", "#ffffff");

    })

    $('#tree').on('ready.jstree', function (e, data) {
            var node = $('#tree').jstree('get_node', String(topic.id), as_dom=true).find('a:first');;
            node.css("background-color", "#00CC4F");
            node.css("color", "#ffffff");

    })
})
