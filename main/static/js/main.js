/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
  document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function get_tree_data(){
    let csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
    let data;
    $.ajax(
         {
             type: 'get',
             url: '/get-tree/',
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

function plot_tree(data){
    $('#tree').jstree({
        'core': {
            'data': data[0]
        }
    });
}

/* Open when someone clicks on the span element */
function openNav() {
    if (window.screen.width <= 1395){
        document.getElementById("mySidenav").style.width = "100%";
        document.getElementById("main").style.marginLeft = "100%";
    }
    else{
        document.getElementById("mySidenav").style.width = "30%";
        document.getElementById("main").style.marginLeft = "30%";
    }
    document.getElementById("toggler").classList.toggle("change");
}

/* Close when someone clicks on the "x" symbol inside the overlay */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0%";
  document.getElementById("main").style.marginLeft = "0px";
  document.getElementById("toggler").classList.toggle("change");
}

function menu_opener(x){
    if (x.classList.value.includes('change')){
        closeNav();
    }
    else{
        openNav();
    }
}

function open_side_menu(){
    let el = document.getElementById("toggler");
    if (el.classList.value.includes('change')){
        closeNav();
    }
    else{
        openNav();
    }
}


document.addEventListener("DOMContentLoaded", function(event) {
    plot_tree(get_tree_data());
    //openNav();

    $('#tree')
        // listen for event
        .on('changed.jstree', function (e, data) {
            var i, j, r = [];
            let node = 0;
            for(i = 0, j = data.selected.length; i < j; i++) {
                node = data.instance.get_node(data.selected[i]).data;
            }
            window.location.href = '/topic/' + node;
        })
    document.getElementById("loader").style.display = "none";
})

