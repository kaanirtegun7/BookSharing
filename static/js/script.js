$(document).ready(function() 
{
    function msgInfos(){

        if( $(".msgInfo").css("display") == "block" ) {
            setTimeout(function(){
                $(".msgInfo").hide();
            },2300);
        } else {
        }
        setTimeout(msgInfos,100);
    }
    msgInfos();
})