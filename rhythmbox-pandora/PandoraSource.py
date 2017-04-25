from gi.repository import GObject, RB, GLib

from . import util


class PandoraEntryType(RB.RhythmDBEntryType):
    NAME = "pandora"
    def __init__(self):
        super(PandoraEntryType, self).__init__(name=PandoraEntryType.NAME,
                                               save_to_disk=False,
                                               category=RB.RhythmDBEntryCategory.STREAM)


class PandoraSource(RB.DisplayPage):
    def __init__(self, **kwargs):
        super(PandoraSource, self).__init__(name="Pandora Radio",
                                            **kwargs)

        group = RB.DisplayPageGroup.get_by_id("library")
        self.props.shell.append_display_page(self, group)
        
        self.stations = []
        # only add radio stations after the connection was established
        self.props.plugin.pandora.add_done_callback(util.from_main_thread_callback(self.add_radio_station_sources))
        
    def add_radio_station_sources(self, *ignore):
        for station in self.props.plugin.pandora.result().stations:
            self.stations.append(PandoraRadioStationSource(parent=self,
                                                           station=station,
                                                           plugin=self.props.plugin,
                                                           shell=self.props.shell
                                                           ))


class PandoraPlayOrder(RB.PlayOrder):
    def __init__(self, *args, **kwargs):
        super(PandoraPlayOrder,self).__init__(*args, **kwargs)
    
    def do_get_previous(self):
        return None
    
    def do_get_next(self):
        query_model = self.get_query_model()
        playing_entry = self.get_playing_entry()
        if playing_entry:
            return query_model.get_next_from_entry(playing_entry)
        else:
            first = query_model.get_iter_first()
            if first:
                return query_model.iter_to_entry(first)
        return None


class PandoraRadioStationSource(RB.StreamingSource):
    def __init__(self, *, parent, station, shell, **kwargs):
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
        
        self._play_order = PandoraPlayOrder(player=self.props.shell.props.shell_player)
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
    
    @GObject.Property(type=RB.PlayOrder)
    def play_order(self):
        return self._play_order
    
    def do_selected(self):
        self.add_songs()
    
    def do_get_playback_status(self, text, progress):
        return self.get_progress()
    
    def do_get_entry_view(self):
        return self.entry_view
    
    def do_can_pause(self):
        return True
    
    def do_handle_eos(self):
        return RB.SourceEOFType.NEXT
    
    def do_try_playlist(self):
        return False
    
    def add_songs(self):
        db = self.props.shell.props.db
        def commit_playlist(pl_future):
            playlist = pl_future.result()
            
            entry_type = db.entry_type_get_by_name(PandoraEntryType.NAME)
            for song in playlist:
                entry = RB.RhythmDBEntry.new(db=db,
                                             type=entry_type,
                                             uri=song.audioUrl)
                db.entry_set(entry, RB.RhythmDBPropType.TITLE, str(song.title))
                db.entry_set(entry, RB.RhythmDBPropType.ARTIST, str(song.artist))
                db.entry_set(entry, RB.RhythmDBPropType.ALBUM, str(song.album))
                
                self.query_model.add_entry(entry, -1)
    
            db.commit()
        
        playlist = self.props.plugin.worker.submit(self.station.get_playlist)
        playlist.add_done_callback(util.from_main_thread_callback(commit_playlist))
