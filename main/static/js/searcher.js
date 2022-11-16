    let query = document.getElementById("query")
    query.addEventListener('input', (e) => {
      e.preventDefault();
      let searchItem = document.getElementsByClassName('content');
      Array.from(searchItem).forEach(function (element) {
        inputVal = query.value.toLowerCase();
        //if includes then show
        if (element.classList.contains("card-body")) {
          if (element.innerHTML.toLowerCase().includes(inputVal) === false) {
            element.parentElement.style.display = "none";
          } else {
            element.parentElement.style.display = "";
          }
        } else {
          if (element.innerHTML.toLowerCase().includes(inputVal) === false) {
            element.style.display = "none";
          } else {
            element.style.display = "";
          }
        }
      });
    });