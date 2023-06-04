$('.form-check-input').click(function(){
    const id = $(this).data("id")
    let correct = false
    if($(this).is(':checked')){
        correct = true
    }

    fetch("/correct", {
        method: "POST",
        headers: { "X-CSRFToken": csrf_token, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        body: `id=${id}&correct=${correct}`,
    }).then((response) => {
        if (response.ok) {
            response.json().then((data) => {
                if (data.correct == "true"){
                    correct = true
                } else {
                    correct = false
                }
                this.checked = correct
                console.log(data)
            })
            console.log("OK")
        } else {
            console.log("FAIL")
        }
    });
});