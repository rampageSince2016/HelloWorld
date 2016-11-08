$EVENT = {};
$INIT = {};

$EVENT.triggerModal = function(){
    $("#windowsXp").modal();
};

$EVENT.register = function() {
    $("#windowsXp").on('hidden.bs.modal', function(){
        alert('怎么回事?');
    });
    $("#tryPop").on('click.bs.popover', function(){
        $("#tryPop").popover();
    });
    $("#tryAppend").on('click', function(){
        var insertHtml = "<div class='panel panel-default'> "    +
                        "   <div class='panel-heading'> abc </div>"  +
                        "   <div class='panel-body'> defg </div>"   +
                        "</div> ";
        $("#tryAppend").before(insertHtml);
    });
    $("#tryDelete").on('click', function(){
        $("#tryAppend").empty();
        //$("#tryAppend").remove();
    });
    $("#tryAlterElemClass").on('click', function(){
        $("#tryDelete").removeClass('btn-info');
        $("#tryDelete").addClass('btn-danger');
    });
};

$(document).ready(function(){
    $EVENT.register();
});
