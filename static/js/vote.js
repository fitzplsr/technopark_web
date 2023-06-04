$(".like").on("click", function (ev) {
    const id = $(this).data("id")
    const vote = $(this).data("vote")
    const type = $(this).data("type")
    var component = $(`.${type}_${id}`);

    fetch("/vote", {
        method: "POST",
        headers: { "X-CSRFToken": csrf_token, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        body: `id=${id}&vote=${vote}&type=${type}`,
    }).then((response) => {
        if (response.ok) {
            response.json().then((data) => {
                component.text(data.likes)
                console.log(data)
            })
            console.log("OK")
        } else {
            console.log("FAIL")
        }
    });
});