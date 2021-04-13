#from datetime import date, datetime, time, timedelta
import datetime as dt
import time
from .models import Timer, Toernooi, Ronde, Team, Notification
from django.shortcuts import get_object_or_404
from django.utils import timezone
import threading
import logging

class Clock:
    """
    1. set clock
        - sets amount of minutes as stringyfied timedelta in database
        - active set to 0
    2. start clock
        - get current time
        - get timedelta from database
        - set endtime as current time + timedelta
        - set active to 1
    3. pause clock
        - get new delta between endtime and current time
        - set active to 0
        - set new delta in database as current timer time

    This way the clocks are synced between all devices because the time
    left is calculated on the client based on the endtime in the database
    """

    def __init__(self, tournament_code):
        self.minutes = 0
        self.hours = 0
        self.time_object = None
        self.duration = 0
        self.endtime = None
        self.tournament_code = tournament_code


    def check_timer_finish(self):
        logging.critical("timer check running")

        while self.timerModel.active == 1:
            self.getCurrent()
            end = False

            if (self.timerModel.eindtijd <= timezone.now()):
                end = True

            if end:
                tournament = get_object_or_404(Toernooi, pk=self.tournament_code)

                # delete all notifications at the end of each round
                Notification.objects.filter(toernooicode=tournament).delete()

                current_round = tournament.current_round              
                current_round += 1

                tournament.current_round = current_round
                tournament.save()

                self.reset()

                logging.critical("timer finished")
                break

            time.sleep(2)

        logging.critical("timer thread stopped")


    def start(self):
        current_time = dt.datetime.now()
        self.duration = self.getCurrent()

        self.endtime = current_time + self.duration

        if self.timerModel.active == 0 and self.timerModel.set == 1:
            # set endtime in database timer model
            self.timerModel.eindtijd = str(self.endtime)

            round_duration = dt.timedelta(minutes=self.getCurrentRoundDuration())

            logging.critical(round_duration)
            logging.critical(self.duration)
            
            # it means the timer has not been started before
            if self.duration == round_duration:
                # set current time as starttime in timer model
                self.timerModel.start_time = current_time

            # set active to 1 in database timer model
            self.timerModel.active = 1
            self.timerModel.save()

        # start thread to watch when the timer finishes
        self.checkTimer = True
        t = threading.Thread(target=self.check_timer_finish, args=[], daemon=True)
        t.start()

        return self.endtime


    def pause(self):
        self.getCurrent()
        current_time = timezone.now()

        # check if active
        if self.timerModel.active == 1:
            # get delta between endtime and current time
            endtime = self.timerModel.eindtijd
            delta = endtime - current_time

            # set active to 0
            self.timerModel.active = 0

            # set current_timer_time to delta
            self.timerModel.current_timer_time = str(delta)

        else:
            # set active to 1
            self.timerModel.active = 1

            # set endtime to current_time + current_timer_time
            self.timerModel.eindtijd = current_time + self.timerModel.current_timer_time

        self.timerModel.save()


    def getCurrent(self):
        self.timerModel = get_object_or_404(Timer, pk=self.tournament_code)
        timedelta = dt.datetime.combine(dt.date.min, self.timerModel.current_timer_time) - dt.datetime.min

        return timedelta


    def set(self, minutes):
        if minutes >= 0:
            try:
                self.time_object = dt.timedelta(minutes=minutes)
                self.timerModel = get_object_or_404(Timer, pk=self.tournament_code)

            except:
                return False
        else:
            raise(Exception("minutes must be > 0"))

        self.hours = self.time_object.seconds//3600
        self.minutes = (self.time_object.seconds//60)%60

        # set current_timer_time to timedelta
        self.timerModel.current_timer_time = str(self.time_object)

        # make sure active is 0
        self.timerModel.active = 0

        if minutes > 0:
            self.timerModel.set = 1
        else:
            self.timerModel.set = 0

        # save changes to database
        self.timerModel.save()


    def getCurrentRoundDuration(self):
        tournament = get_object_or_404(Toernooi, pk=self.tournament_code)
        rounds = Ronde.objects.filter(toernooicode=self.tournament_code)

        # get current round
        current_round = rounds.filter(rondenummer=tournament.current_round)

        if current_round.count() == 1:
            for round in current_round:
                current_round = round

            # get duration of that round
            round_duration = current_round.duratie
        else:
            round_duration = 0

        return round_duration


    def reset(self):
        self.getCurrent()
        self.start_time = None
        self.eindtijd = None
        self.set(self.getCurrentRoundDuration())
        self.timerModel.save()


    def __str__(self):
        return str(self.hours).zfill(2) + ':' + str(self.minutes).zfill(2) + ':00'