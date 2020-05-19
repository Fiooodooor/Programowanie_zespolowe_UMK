$(document).ready(function () {
    var focusrepass=0;
    $('#repassid').on('focus',function () {
        focusrepass=1;
    });
    $('#repassid').on('change',function () {
            if($('#repassid').val()!=$('#passid').val()){
                $('#repassidAlert').removeClass('d-none'); //f2dede
            }
            else {
                 $('#repassidAlert').addClass('d-none');
            }
    });
})