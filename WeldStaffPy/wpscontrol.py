# -*- coding: utf-8 -*-

from base import BaseControl


class WPSControl(BaseControl):
    def __init__(self):
        BaseControl.__init__(self)
        self.table = self.db.WPSTable
