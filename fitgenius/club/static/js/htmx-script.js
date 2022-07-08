;(function () {
    const myModal = new bootstrap.Modal(document.getElementById("modal"))
    htmx.on('htmx:afterSwap', (e) => {


        if (e.target.id === 'offer-table-body' || e.target.id === 'action-table-body') {
            $(document).ready(function () {
                $(".datatable").DataTable({
                    "order": [],
                    'responsive': false
                })
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
