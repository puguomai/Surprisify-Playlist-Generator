var open_btn = document.getElementById('options');
var close_btn = document.querySelector('.close');
var submit_btn = document.getElementById('pl_submit');
var pl_name = document.getElementById('playlist-name');
var pl_desc = document.getElementById('playlist-description');
var modal = document.querySelector('.modal');



open_btn.addEventListener('click', ()=> {
    modal.classList.add('modal-active');
});

close_btn.addEventListener('click', ()=> {
    modal.classList.remove('modal-active');
    pl_name.value = "";
    pl_desc.value = "";

});


$(document).ready(function() {
    $('#pl_submit').on('click', ()=> {
        event.preventDefault();
        modal.classList.remove('modal-active');
        var name = $('#playlist-name').val();
        var desc = $('#playlist-description').val();

        req = $.ajax({
            url : '/update',
            type : 'POST',
            data : { name : name, desc : desc}
        });        

    });
});



pl_name.addEventListener('keypress', function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
    });


window.onclick = function(event) {
    if (event.target == modal) {
        modal.classList.remove('modal-active');

    }
}