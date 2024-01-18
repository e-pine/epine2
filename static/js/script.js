// Extensionn of all pages 
// 1. script to confirm save changes (if it exist)
$(document).ready(function(){
    $("#btn-back").click(function() {

        var product = $("#product").val();
        var purchase = $("#purchase").val();
        var sale = $("#sale").val();
        var qty = $("#qty").val();  
        var gender = $("#gender").val();
        var note = $("#product").val();
// hidden input
        var product2 = $("#product2").val();
        var purchase2 = $("#purchase2").val();
        var sale2 = $("#sale2").val();
        var qty2 = $("#qty2").val();
        var gender2 = $("#gender2").val();
        var note2 = $("#product2").val();

        if ( (product != product2) || (purchase != purchase2) || 
             (sale != sale2) || (qty != qty2) || (gender != gender2) || (note != note2) ) {
                // buttom to call modal
              $("#modal-confirm").trigger('click');
              return false;
        }
    });
});