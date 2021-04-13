function setClock() {
    //
    // temporarily disabled
    //

    // minutes = prompt("Hoeveel minuten?");

    if (minutes > 0 && minutes < 1440) {
        // window.location.href = "timer/set/" + minutes;
    }
    else {
        // setClock();
    }
}

timer = (function ($) {

    let clock = {};

    const init = function () {
        update();
        setInterval(update, 1000);
    };

    const update = function () {
        $.ajax({
            'url': 'timer',
            'dataType': 'json',
            'async': true,
            'success': function (data) {
                clock = data;
                updateButtons();
                updateData();                
            }
        });
    };

    const updateData = function () {
        endtime = new Date(Date.parse(clock.endtime));
        round = "";

        if (clock.round == -1) {
            round = "Einde Toernooi";
        }
        else {
            round = "Ronde: " + clock.round;
        }

        $('#timerContainer').html(calculate());
        $('#eindtijd').html("Eindtijd: " + endtime.getHours() + ":" + endtime.getMinutes() + ":" + endtime.getSeconds());
        $('#rounds').html(round);
    }

    const updateButtons = function () {
        if (clock.active == 1) {
            $('#eindtijd').css('display', 'inline');
            $('#pause').css('display', 'inline');
            $('#reset').css('display', 'inline');
            $('#start').css('display', 'none');
            $('#restart').css('display', 'none');
        }
        else {
            $('#eindtijd').css('display', 'none');
            $('#pause').css('display', 'none');
            $('#restart').css('display', 'inline');
            $('#reset').css('display', 'none');

            if (clock.set == 1) {
                $('#start').css('display', 'inline');
            }
            else {
                $('#reset').css('display', 'none');
                $('#start').css('display', 'none');
            }
        }
    }

    const calculate = function () {
        if (clock.active == 1) {
            endtime = new Date(Date.parse(clock.endtime));
            now = Date.now();

            diffInSec = Math.round((endtime - now) / 1000);

            timeLeft = new Date(diffInSec * 1000).toISOString().substr(11, 8);
        }
        else {
            if (clock.set == 1) {
                const current_timer_time = clock.current_timer_time;
                timeLeft = current_timer_time.substr(0, 8);
            }
            else {
                timeLeft = "00:00:00";
            }
        }

        return timeLeft;
    };

    return {
        init: init
    };

})($);