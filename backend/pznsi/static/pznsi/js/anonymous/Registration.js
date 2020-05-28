$(document).ready(function () {
    var focusrepass=0;
    $('#passid').on('focus',function () {
        focusrepass=1;
        $('#message').show();
    });
    $('#passid').on('blur',function () {
        focusrepass=1;
        $('#message').hide();
    });
    $('#repassid').on('keyup',function () {
            if($('#repassid').val()!=$('#passid').val()){
                $('#repassidAlert').removeClass('d-none'); //f2dede
            }
            else {
                 $('#repassidAlert').addClass('d-none');
            }
    });
    var lowerCaseLetters = /[a-z]/g;
    var upperCaseLetters = /[A-Z]/g;
    var numbers = /[0-9]/g;
    $('#passid').on('keyup',function () {
        $('#signinBtn').prop('disabled', true);
        var sumMatch=0;
        $('.matchPassword').hide();
        $('#message').hide();
        myInput=document.getElementById('passid');
        if(!myInput.value.match(numbers)){
            $('#minJML').show();
            sumMatch++;
        }
        if(!myInput.value.match(lowerCaseLetters)){
            $('#minML').show();
            sumMatch++;
        }
        if(!myInput.value.match(upperCaseLetters)){
            $('#minWL').show();
            sumMatch++;
        }
        if(myInput.value.length<8){
            $('#min8').show();
            sumMatch++;
        }
        if(sumMatch!=0){
             $('#message').show();
        }
        else {
           $('#signinBtn').prop('disabled', false);
        }
    });
});