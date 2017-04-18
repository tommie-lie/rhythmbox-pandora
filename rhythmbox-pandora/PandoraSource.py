from gi.repository import GObject, RB

class PandoraEntryType(RB.RhythmDBEntryType):
    NAME = "pandora"
    def __init__(self):
        super(PandoraEntryType, self).__init__(name=PandoraEntryType.NAME)


class PandoraSource(RB.DisplayPage):
    def __init__(self, **kwargs):
        super(PandoraSource, self).__init__(name="Pandora Radio",
                                            **kwargs)

        group = RB.DisplayPageGroup.get_by_id("library")
        self.props.shell.append_display_page(self, group)
        
        self.stations = []
        # only add radio stations after the connection was established
        self.props.plugin.pandora.add_done_callback(self.add_radio_station_sources)
        
    def add_radio_station_sources(self, *ignore):
        for station in self.props.plugin.pandora.result().stations:
            self.stations.append(PandoraRadioStationSource(parent=self,
                                                           station=station,
                                                           plugin=self.props.plugin,
                                                           shell=self.props.shell
                                                           ))


class PandoraRadioStationSource(RB.StreamingSource):
    def __init__(self, parent, station, shell, **kwargs):
        if not parent:
            raise ValueError("parent argument must not be null")
        if not station:
            raise ValueError("station argument must not be null")
        
        self.station = station
        et = shell.props.db.entry_type_get_by_name(PandoraEntryType.NAME)
        if not et:
            et = PandoraEntryType()
            shell.props.db.register_entry_type(et)
        super(PandoraRadioStationSource, self).__init__(name=station.name,
                                                        entry_type=et,
                                                        parent=parent,
                                                        shell=shell,
                                                        **kwargs)
        
        self.query_model = RB.RhythmDBQueryModel.new_empty(self.props.shell.props.db)
        self.props.query_model = self.query_model
        
        self.entry_view = RB.EntryView(db=self.props.shell.props.db,
                                       shell_player=self.props.shell.props.shell_player,
                                       is_drag_source=False,
                                       is_drag_dest=False)
        self.entry_view.append_column(RB.EntryViewColumn.TITLE, True)
        self.entry_view.append_column(RB.EntryViewColumn.ARTIST, True)
        self.entry_view.append_column(RB.EntryViewColumn.ALBUM, True)
        self.entry_view.set_model(self.props.query_model)
        self.entry_view.show_all()
        self.pack_start(self.entry_view, expand=True, fill=True, padding=0)        

        self.props.shell.append_display_page(self, parent)
    
    def do_get_entry_view(self):
        return self.entry_view
