from gi.repository import GObject, RB

class PandoraEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        super(PandoraEntryType, self).__init__(name="pandora")

class PandoraSource(RB.StreamingSource):
    def __init__(self, **kwargs):
        et = PandoraEntryType()
        super(PandoraSource, self).__init__(name="Pandora Radio",
                                            entry_type=et,
                                            **kwargs)
        db = self.props.shell.props.db
        db.register_entry_type(self.props.entry_type)

        group = RB.DisplayPageGroup.get_by_id("library")
        self.props.shell.append_display_page(self, group)
        self.props.shell.register_entry_type_for_source(self, self.props.entry_type)
