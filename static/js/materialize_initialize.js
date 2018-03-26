function materialize_initiailize() {
    $('.collapsible').collapsible();
    $(".button-collapse").sideNav();
    $('select').material_select();
    $('ul.tabs').tabs({'swipeable': true});
    $('.datepicker').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 199, // Creates a dropdown of 15 years to control year,
        today: 'Today',
        clear: 'Clear',
        close: 'Ok',
        closeOnSelect: false,
        format: 'yyyy-mm-dd'
    })
};
