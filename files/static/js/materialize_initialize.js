function materialize_initiailize() {
    // M.AutoInit();
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.sidenav').sidenav();
    $('.datepicker').datepicker({
        selectMonths: true, // Creates a dropdown to control month
        yearRange: [1900, 2030],// Creates a dropdown of 15 years to control year,
        today: 'Today',
        clear: 'Clear',
        close: 'Ok',
        closeOnSelect: false,
        format: 'yyyy-mm-dd',
        autoClose: true,
    });
    M.Tooltip.init($('.tooltipped'), {});
    $('#modal').modal();
    $('#modal').hide();
}
