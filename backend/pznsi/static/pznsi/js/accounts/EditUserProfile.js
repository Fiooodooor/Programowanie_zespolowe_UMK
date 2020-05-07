var $uploadCrop, tempFilename, rawImg, imageId;
$(document).ready(function () {
    $("[data-toggle=popover]").popover();
    function readFile(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('.upload-demo').addClass('ready');
                $('#crupperModal').modal('show');
                rawImg = e.target.result;
            }
            reader.readAsDataURL(input.files[0]);
        } else {
            swal("Sorry - you're browser doesn't support the FileReader API");
        }
    }

    $uploadCrop = $('#upload-demo').croppie({
        viewport: {
            width: 200,
            height: 200
            //,type: 'circle'  pczycina zdjęcie w kółko, wyświetlanie zdjęcia nie może być zaokrąglone
        },
        enforceBoundary: false,
        enableExif: true,
        type: 'circle'
    });

    $('#imgInp').on('click', function () {
        $('#imgInp').val("");
    });

    $('#imgInp').on('change', function () {
        imageId = $(this).data('id');
        tempFilename = $(this).val();
        // $('#cancelCropBtn').data('id', imageId);
        readFile(this);
    });
    $('#crupperModal').on('shown.bs.modal', function () {
        // alert('Shown pop');
        $uploadCrop.croppie('bind', {
            url: rawImg
        });
    });
    $('#cropImageBtn').on('click', function (ev) {
        $uploadCrop.croppie('result', {
            type: 'base64',
            format: 'jpeg',
            size: {width: 150, height: 200}
        }).then(function (resp) {
            $('#ImgAvatar').attr('src', resp);
            $('#avatarField').attr('value', resp);
            $('#crupperModal').modal('hide');
        });
    });
    $('#ImgAvatar').on('click', function (ev) {
        imgInp.click();
    });
});