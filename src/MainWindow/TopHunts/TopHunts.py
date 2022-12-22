from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QScrollArea, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from resources import *
from DbHandler import *

sortOpts = ["your_kills","team_kills","your_deaths","assists"]
#todo = ["xp","event_points","monster_kills","hunt_dollars"]

class TopHunts(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.initOptions()

        self.body = QWidget()
        self.body.layout = QVBoxLayout()
        self.body.setLayout(self.body.layout)

        self.main.layout.addWidget(self.body)
        self.setWidget(self.main)

        self.main.layout.addStretch()

    def initOptions(self):
        self.opts = QWidget()
        self.opts.layout = QGridLayout()
        self.opts.setLayout(self.opts.layout)
        self.opts.layout.addWidget(QLabel("Sort By"),0,0)
        self.opts.layout.addWidget(QLabel("Results"),0,1)

        self.sortingSelect = QComboBox()

        for opt in sortOpts:
            self.sortingSelect.addItem(getLabel(opt),opt)

        self.numResults = QComboBox()
        self.numResults.addItems(str(i) for i in [1,5,10,20,50,100])
        self.numResults.setCurrentText('10')
        self.numResults.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.opts.layout.addWidget(self.sortingSelect,1,0)
        self.opts.layout.addWidget(self.numResults,1,1)

        self.submit = QPushButton("Update")
        self.submit.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.submit.clicked.connect(self.update)
        self.opts.layout.addWidget(self.submit,1,2)

        self.main.layout.addWidget(self.opts)

    def update(self):
        if debug:
            print('tophunts.update')
        clearLayout(self.body.layout)
        sort = self.sortingSelect.currentData()
        num = int(self.numResults.currentText())

        hunts = GetHunts()
        if sort == 'your_kills':
            func = getYourKillCount
        elif sort == 'your_deaths':
            func = getYourDeathCount
        elif sort == 'team_kills':
            func = getTeamKillCount
        elif sort == 'assists':
            func = getAssists
        for hunt in hunts:
            ts = hunt['timestamp']
            hunt[sort] = func(ts)
        hunts = sorted(hunts,key= lambda i : i[sort],reverse=True)[:num]

        for hunt in hunts:
            widget = self.HuntWidget(hunt)
            self.body.layout.addWidget(widget)
            #self.body.addTopLevelItem(item)
            #self.body.setItemWidget(item,0,widget)
    
    def HuntWidget(self,data):
        ts = data['timestamp']
        w = QWidget()
        w.layout = QVBoxLayout()
        w.setLayout(w.layout)

        w.main = QWidget()
        w.main.layout = QGridLayout()
        w.main.setLayout(w.main.layout)
        headerBtn = QPushButton(unix_to_datetime(ts))
        headerBtn.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        headerBtn.setObjectName("link")
        w.layout.addWidget(headerBtn)
        headerBtn.clicked.connect(lambda : GoToHuntPage(data['timestamp'],main=self.window().mainframe))
        MatchButton = QPushButton("View Details...")
        MatchButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        MatchButton.clicked.connect(lambda : GoToHuntPage(data['timestamp'],main=self.window().mainframe))

        isQp = str(data['MissionBagIsQuickPlay']).lower() == "true"
        numTeams = int(data['MissionBagNumTeams'])
        bounties = GetBounties(data)
        survived = str(data['MissionBagIsHunterDead']).lower() != "true"
        teams = GetTeams(ts)
        hunters = GetHunters(ts)
        accolades = GetHuntAccolades(ts)
        killData = getKillData(ts)
        team_kills = killData['team_kills']
        your_kills = killData['your_kills']
        your_deaths = killData['your_deaths']
        assists = killData['assists']
        yourKills = QLabel(
            "Your kills: %d<br>%s" % (
                sum(your_kills.values()),
                '<br>'.join(["%sx %s" % (
                    your_kills[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_kills.keys() if your_kills[stars] > 0])
            )
        )
        yourDeaths = QLabel(
            "Your deaths: %d<br>%s" % (
                sum(your_deaths.values()),
                '<br>'.join(["%sx %s" % (
                    your_deaths[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_deaths.keys() if your_deaths[stars] > 0])
            )
        )
        w.main.layout.addWidget(QLabel("Quickplay" if isQp else "Bounty Hunt"),0,0,Qt.AlignmentFlag.AlignTop)
        w.main.layout.addWidget(QLabel("%d %s" % (numTeams, "teams" if not isQp else "hunters")),1,0,Qt.AlignmentFlag.AlignTop)
        if not isQp:
            w.main.layout.addWidget(QLabel(", ".join(bounties)),2,0,Qt.AlignmentFlag.AlignTop)
        if not isQp:
            teamKills = QLabel(
                "Team kills: %d<br>%s" % (
                    sum(team_kills.values()),
                    '<br>'.join(["%sx %s" % (
                        team_kills[stars],
                        "<img src='%s'>" % (star_path())*stars
                    ) for stars in team_kills.keys() if team_kills[stars] > 0])
                )
            )
            w.main.layout.addWidget(teamKills,0,1,Qt.AlignmentFlag.AlignTop)
        else:
            w.main.layout.addWidget(QLabel(),0,1,Qt.AlignmentFlag.AlignTop)
        w.main.layout.addWidget(yourKills,0,2,Qt.AlignmentFlag.AlignTop)
        w.main.layout.addWidget(yourDeaths,0,3, Qt.AlignmentFlag.AlignTop)
        w.main.layout.addWidget(QLabel("%d assists." % assists),0,4,Qt.AlignmentFlag.AlignTop)
        
        sort = self.sortingSelect.currentData()
        w.layout.addWidget(QLabel("%s: %d" % (getLabel(sort),data[sort])))
        w.layout.addWidget(w.main)
        w.layout.addWidget(MatchButton)

        w.main.setVisible(True)
        w.setObjectName("HuntWidget")
        return w

def toggle(widget : QWidget, btn : QPushButton):
    if widget.isVisible():
        widget.setHidden(True)
        btn.setIcon(QIcon(resource_path("assets/icons/plus.png")))
    else:
        widget.setVisible(True)
        btn.setIcon(QIcon(resource_path("assets/icons/minus.png")))

def getLabel(txt):
    words = txt.split("_")
    for i in range(len(words)):
        words[i] = words[i].capitalize()
    return " ".join(words)
