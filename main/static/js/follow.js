async function follow(){
    blogsno = $("#blogsno").val()
    $("#follow").attr("disabled", "disabled");
    $("#follow").html(`

  <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
  Loading...
  `);

    var myHeaders = new Headers();
    myHeaders.append(
        "Cookie",
        "Cookie_1=value; Cookie_2=value; session=5a67b465-54b3-4ceb-aff3-496d75f28602"
    );

    var formdata = new FormData();
    formdata.append("sno", blogsno);

    var requestOptions = {
        method: "GET",
        headers: myHeaders,
        credentials: "include",
        redirect: "follow",
    };

    await fetch(
            `/follow?sno=${blogsno}`,
            requestOptions
        )
        .then((response) => response.json())
        .then((result) => {
            if (result["is_follow"]) {
                $("#follow").html('<i class="fa fa-check"></i> Followed');
                $("#follow").removeClass('btn-primary')
                $("#follow").addClass('btn-orange')
            } else {
                $("#follow").html('<i class="fa fa-plus-square-o"></i> Follow');
                $("#follow").removeClass('btn-orange')
                $("#follow").addClass('btn-primary')
            }
            $("#followCount").text(String(result['followCount']));

        })
        .catch((error) => console.log("error", error));
};