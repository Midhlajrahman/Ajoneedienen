// if page has .form-check, add .form-switch to .form-check
$(document).ready(function () {
    if ($('.form-check').length) {
        $('.form-check').addClass('form-switch');
    }
});

$('.dateinput').datepicker({
    format: 'dd/mm/yyyy',
});

$('.datatable').DataTable({
    dom: '<"row"<"col-md-7"B><"col-md-1"l><"col-md-4"f>>rtip',
    info: false,
    paging: false,
    buttons: [
        'copy', 'csv', 'excel', 'pdf', 'print'
    ],
});

$("#id_subcategory").select2();
