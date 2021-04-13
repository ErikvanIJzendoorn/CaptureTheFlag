window.onload = function () {

    var modal = document.getElementById("scheids-modal");

    var btn = document.getElementById("add-scheids-btn");

    var close = document.getElementById("close-scheids-modal");

    btn.onclick = function () {
        modal.style.display = "block";
    }

    close.onclick = function () {
        modal.style.display = "none";
    }
}