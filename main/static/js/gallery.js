function open_gallery_block(block_id){
    console.log(block_id);
    let el = document.getElementById(block_id);

    console.log(el.getAttribute('opened'));

    if (el.getAttribute('opened') == 'true'){
        el.style.display = "none";
        el.setAttribute('opened', false);
    }
    else{
        el.style.display = "block";
        el.setAttribute('opened', true)
    }
}