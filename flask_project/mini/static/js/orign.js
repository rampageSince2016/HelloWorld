$EVENT = {};
$PAGE = {};

$PAGE.init_page = function(){
    $(".my-single-select").select2();
    $(".my-js-mark-up").select2({theme: "classic"});
};

$EVENT.init_event = function(){
    $('a[data-toggle="tab"]').on('click', function(e){
        console.info(e.target);
    });
    $("#shit").on('click', function(){
        alert('shit');
    });
};

$(document).ready(function(){
    $PAGE.init_page();
    $EVENT.init_event();
});
