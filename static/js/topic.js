function prepare_answer(author_name, comment_id){
    console.log(author_name, comment_id);
    let content = CKEDITOR.dom.element.createFromHtml(`<a>${author_name}</a>`);
    let mock = CKEDITOR.dom.element.createFromHtml(`<span>, </span>`);

    CKEDITOR.instances.id_text.insertElement(content);
    CKEDITOR.instances.id_text.insertElement(mock);

    document.getElementById("parentcomment").value = comment_id;

    let answer_el = document.getElementById("answer_to");
    answer_el.style.display = "block"
    answer_el.innerHTML = `<div style="flex-direction: row">
                                <span style="display: inline-block">Ответ пользователю ${author_name}: </span>
                                <a style="display: inline-block; float: right; right: 0; margin-right: 2%; 
                                color: red; cursor: pointer" onclick="cancel_anser()">отмена</a>
                            </div>`;
    console.log(document.getElementById("parentcomment").value);
}

function cancel_anser(){
    let answer_el = document.getElementById("answer_to");
    answer_el.style.display = "none";
    document.getElementById("parentcomment").value = "";
    CKEDITOR.instances.id_text.setData("");
    console.log(document.getElementById("parentcomment").value);
}

function delete_comment(commnet_id, is_comment){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    let url = '';
    let block_name = '';

    if (is_comment){
        url = '/comments/hide/';
        block_name = 'comment_block_' + commnet_id;
    }
    else{
        url = '/answers/delete/';
        block_name = 'comment_answer_block_' + commnet_id;
    }

    $.ajax(
         {
             type: 'post',
             url: url + commnet_id + '/',
             headers: {'X-CSRFToken': csrf_token},
             mode: 'same-origin',
             async: true,
             success : function(json)
             {
                 if (is_comment){
                     document.getElementById("comment_text_" + commnet_id).innerHTML = "<span style=\"color: #858383\">---Комментарий удален модератором---</span><br><br>";
                 }
                 else{
                     document.getElementById("answer_text_" + commnet_id).innerHTML = "<span style=\"color: #858383\">---Комментарий удален модератором---</span><br><br>";
                 }
             },
             error : function(xhr,errmsg,err) {
                alert('Ошибка! ' + xhr.responseText);
             }
         }
     )
}