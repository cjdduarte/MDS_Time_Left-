# -*- coding: utf-8 -*-
#Copyright(C)   | Carlos Duarte
#Based 1 on     | Dmitry Mikheev code, in add-on "More decks overview stats"
#Based 2 on     | calumkscode, in add-on https://github.com/calumks/anki-deck-stats
#License        | GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#Source in      | https://github.com/cjdduarte/MDS_Time_Left

import anki
import aqt
from aqt import mw
from aqt.utils import tooltip

#-------------Configuration------------------
if getattr(getattr(mw, "addonManager", None), "getConfig", None): #Anki 2.1
    config = mw.addonManager.getConfig(__name__)
else:
    # The default steps for "New" Anki cards are 1min and 10min meaning that you see New cards actually a minimum of *TWO* times that day
    # You can now configure how many times new cards will be counted.
    # CountTimesNew = 1 (old version)
    # Quantify '1' time the "new card" time | Example: Steps (10 1440)
    # CountTimesNew = 2 (default)
    # Quantify '2' times the "new card" time | Example: Steps (1 10)
    # CountTimesNew = n
    # Quantify 'n' times the "new card" time | Example: Steps (1 10 10 20 30...)

    #----- Modify here (Anki 2.0) ------
    config = dict(CountTimesNew = 2, NewColor = 'DarkBlue', ReviewColor = 'DarkRed', LearnColor = 'DarkRed', TotalDueColor = 'ForestGreen', TotalColor = 'Grey')
    #----- Modify here (Anki 2.0) ------

CountTimesNew = config['CountTimesNew']
#-------------Configuration------------------


def renderStats(self, _old):
    # Get due and new cards
    new = 0
    lrn = 0
    due = 0

    for tree in self.mw.col.sched.deckDueTree():
        new += tree[4]
        lrn += tree[3]
        due += tree[2]

    #if CountTimesNew == 0: CountTimesNew = 2
    total = (CountTimesNew*new) + lrn + due
    totalDisplay = new + lrn + due
    #total = new + lrn + due

    # Get studdied cards
    cards, thetime = self.mw.col.db.first(
            """select count(), sum(time)/1000 from revlog where id > ?""",
            (self.mw.col.sched.dayCutoff - 86400) * 1000)

    cards   = cards or 0
    thetime = thetime or 0

    speed   = cards * 60 / max(1, thetime)
    minutes = int(total / max(1, speed))

    NewColor        = config['NewColor']
    ReviewColor     = config['ReviewColor']
    LearnColor      = config['LearnColor']
    TotalDueColor   = config['TotalDueColor']
    TotalColor      = config['TotalColor']

    insert_style = "<style type=\"text/css\">" \
        + ".new-color { color:"         + NewColor + ";}" \
        + ".review-color { color:"      + ReviewColor + ";}" \
        + ".learn-color { color:"       + LearnColor + ";}" \
        + ".totaldue-color { color:"    + TotalDueColor + ";}" \
        + ".total-color { color:"       + TotalColor + ";}" \
        + "</style>"

    buf = insert_style \
        + "<div style='display:table;padding-top:1.5em;'>" \
        + "<div style='display:table-cell;'> " \
        + _old(self) + "<hr>" \
        + _("New Cards") \
        + ": &nbsp; <span class='new-color'> %(d)s</span>" % dict(d=new) \
        + " &nbsp; " + _("Learn") \
        + ": &nbsp; <span class='learn-color'>%(c)s</span>" % dict(c=lrn) \
        + " &nbsp; <span style='white-space:nowrap;'>" + _("To Review") \
        + ": &nbsp; <span class='review-color'>%(c)s</span>" % dict(c=due) \
        + "</span>" \
        + " &nbsp; <br><span style='white-space:nowrap;'>" + _("Due") \
        + ": &nbsp; <b class='totaldue-color'>%(c)s</b> " % dict(c=(lrn+due)) \
        + "</span> " \
        + " &nbsp; <span style='white-space:nowrap;'>" + _("Total") \
        + ": &nbsp; <b class='total-color'>%(c)s</b>" % dict(c=(totalDisplay)) \
        + "</span></div>" \
        + "<div style='display:table-cell;vertical-align:middle;" \
        + "padding-left:2em;'>" \
        + "<span style='white-space:nowrap;'>" + _("Average") \
        + ":<br> " + _("%.01f cards/minute") % (speed) \
        + "</span><br><br>" \
        + _("More") + "&nbsp;" + ngettext(
             "%s minute.", "%s minutes.", minutes) % (minutes) \
        + "</div></div>"
    return buf

aqt.deckbrowser.DeckBrowser._renderStats = anki.hooks.wrap(
    aqt.deckbrowser.DeckBrowser._renderStats, renderStats, 'around')