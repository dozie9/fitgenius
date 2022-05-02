;(function () {
    const myModal = new bootstrap.Modal(document.getElementById("modal"))
    htmx.on('htmx:afterSwap', (e) => {


        if (e.target.id === 'offer-table-body') {
            $(document).ready(function () {
                $("#datatable").DataTable(), $("#datatable-buttons").DataTable({
                    lengthChange: !1,
                    buttons: ["copy", "excel", "pdf", "colvis"]
                }).buttons().container().appendTo("#datatable-buttons_wrapper .col-md-6:eq(0)"), $(".dataTables_length select").addClass("form-select form-select-sm")
            });
        }

        if (e.detail.target.id === 'dialog') {
            myModal.show()
        }
    })

    htmx.on('htmx:beforeSwap', (e) => {
        if (e.detail.target.id === 'dialog' && !e.detail.xhr.response) {
            myModal.hide()
        }
    })

})()
