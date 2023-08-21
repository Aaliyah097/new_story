function get_bookmarks(){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax(
         {
             type: 'get',
             url: '/bookmarks',
             headers: {'X-CSRFToken': csrf_token},
             mode: 'same-origin',
             async: true,
             success : function(json)
             {
               let el = document.getElementById("booksmark_modal");
               let data = JSON.parse(json);

               for (let slug in data) {
                   el.innerHTML += `
                    <div style="flex-direction: row;" id="bookmark_${slug}">
                            <a href="/topic/${slug}" style="display: inline-block">${data[slug]}</a>
                            <form method="post" action="/bookmarks/remove/${slug}/" style="display: inline-block; float: right">
                                <a style=" float: right; color: red; font-size: 14px; cursor: pointer"
                                 onclick="delete_bookmark('${slug}')">удалить</a>
                            </form>
                            <hr>
                        </div>
                   `
               }
             },
             error : function(xhr,errmsg,err) {
                alert('Ошибка!', 'Повторите попытку позднее.');
             }
         }
     )
}

function delete_bookmark(slug){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax(
         {
             type: 'post',
             url: '/bookmarks/remove/' + slug + '/',
             headers: {'X-CSRFToken': csrf_token},
             mode: 'same-origin',
             async: true,
             success : function(json)
             {
               let el = document.getElementById("bookmark_" + slug);
               el.remove();
             },
             error : function(xhr,errmsg,err) {
                alert('Ошибка!', 'Повторите попытку позднее.');
             }
         }
     )
}
