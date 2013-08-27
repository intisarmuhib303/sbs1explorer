#    Copyright (C) 2008 Vasco Costa <vasco dot costa at geekslot dot com>
#
#    This file is part of sbs1explorer.
#
#    sbs1explorer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    sbs1explorer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


import threading

import wx
import wx.grid

import constants
import business


PROGRAM_NAME = 'SBS1 Explorer'
PROGRAM_VERSION = 'v0.2.1'
PROGRAM_AUTHOR = 'Vasco Costa <vasco dot costa at geekslot dot com>'

ID_MENU_FILE_OPEN = 1
ID_MENU_FILE_EXIT = 2
ID_MENU_DATABASE_INFO = 3
ID_MENU_DATABASE_SEARCH = 4
ID_MENU_DATABASE_CLEAR = 5
ID_MENU_HELP_HELP = 6
ID_MENU_HELP_ABOUT = 7
ID_BUTTON_SEARCH = 8
ID_BUTTON_CLEAR = 9
ID_BUTTON_STOP = 10
ID_EVT_RESULT = 11


def EVT_RESULT(win, func):
    win.Connect(-1, -1, ID_EVT_RESULT, func)


class ResultEvent(wx.PyEvent):

    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(ID_EVT_RESULT)
        self.data = data


class SearchThread(threading.Thread):

    def __init__(self, notify_window, database_path, data):
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self.database_path = database_path
        self.data = data
        self._want_abort = 0
        self.start()

    def run(self):
        aircraft_controller = business.AircraftController(self.database_path)
        try:
            aircraft_controller.search(self.data)
            wx.PostEvent(self._notify_window, ResultEvent(aircraft_controller.results))
        except business.DatabaseError, e:
            wx.PostEvent(self._notify_window, ResultEvent([]))

    def abort(self):
        self._want_abort = 1


class MainWindow(wx.Frame):

    def __init__(self, parent, id, title, size=(800, 600)):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(800, 600))
        # menu widgets
        self.menu_file = wx.Menu()
        self.menu_database = wx.Menu()
        self.menu_options = wx.Menu()
        self.menu_help = wx.Menu()
        self.menu_file.Append(ID_MENU_FILE_OPEN, '&Open...', 'Open base station database.')
        self.menu_file.AppendSeparator()
        self.menu_file.Append(ID_MENU_FILE_EXIT, 'E&xit', 'Terminate the program.')
        self.menu_database.Append(ID_MENU_DATABASE_INFO, '&Info', 'Display database information.')
        self.menu_database.Append(ID_MENU_DATABASE_SEARCH, '&Search', 'Query the database.')
        self.menu_database.Append(ID_MENU_DATABASE_CLEAR, '&Clear', 'Clear the search fields.')
        self.menu_help.Append(ID_MENU_HELP_HELP, '&Help', 'Display help information.')
        self.menu_help.AppendSeparator()
        self.menu_help.Append(ID_MENU_HELP_ABOUT, '&About ' + PROGRAM_NAME, 'Display About information.')
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(self.menu_file, '&File')
        self.menu_bar.Append(self.menu_database, '&Database')
        self.menu_bar.Append(self.menu_options, '&Options')
        self.menu_bar.Append(self.menu_help, '&Help')
        self.menu_database.Enable(ID_MENU_DATABASE_INFO, False)
        # static text widgets
        self.static_text_squawk = wx.StaticText(self, -1, 'Squawk:', style=wx.ALIGN_LEFT)
        self.static_text_callsign = wx.StaticText(self, -1, 'Callsign:', style=wx.ALIGN_LEFT)
        self.static_text_alert = wx.StaticText(self, -1, 'Alert:', style=wx.ALIGN_LEFT)
        self.static_text_emergency = wx.StaticText(self, -1, 'Emergency:', style=wx.ALIGN_LEFT)
        self.static_text_spi = wx.StaticText(self, -1, 'SPI:', style=wx.ALIGN_LEFT)
        self.static_text_modes = wx.StaticText(self, -1, 'ModeS:', style=wx.ALIGN_LEFT)
        self.static_text_registration = wx.StaticText(self, -1, 'Registration:', style=wx.ALIGN_LEFT)
        self.static_text_type = wx.StaticText(self, -1, 'Type:', style=wx.ALIGN_LEFT)
        self.static_text_operator = wx.StaticText(self, -1, 'Operator:', style=wx.ALIGN_LEFT)
        self.static_text_country = wx.StaticText(self, -1, 'Country:', style=wx.ALIGN_LEFT)
        # text ctrl widgets
        self.text_ctrl_squawk = wx.TextCtrl(self, -1)
        self.text_ctrl_callsign = wx.TextCtrl(self, -1)
        self.text_ctrl_modes = wx.TextCtrl(self, -1)
        self.text_ctrl_registration = wx.TextCtrl(self, -1)
        self.text_ctrl_operator = wx.TextCtrl(self, -1)
        self.text_ctrl_squawk.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.text_ctrl_callsign.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.text_ctrl_modes.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.text_ctrl_registration.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.text_ctrl_operator.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        # combo box widgets
        self.combo_box_alert = wx.ComboBox(self, -1, choices=('True', 'False'))
        self.combo_box_emergency = wx.ComboBox(self, -1, choices=('True', 'False'))
        self.combo_box_spi = wx.ComboBox(self, -1, choices=('True', 'False'))
        self.combo_box_type = wx.ComboBox(self, -1, choices=constants.ICAO_TYPE_CODES)
        self.combo_box_country = wx.ComboBox(self, -1, choices=constants.COUNTRIES)
        self.combo_box_alert.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.combo_box_emergency.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.combo_box_spi.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.combo_box_type.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.combo_box_country.SetToolTip(wx.ToolTip('You can use SQL wildcards like % and _.'))
        self.combo_box_alert.Enable(False)
        self.combo_box_emergency.Enable(False)
        self.combo_box_spi.Enable(False)
        # grid widgets
        self.grid_results = wx.grid.Grid(self)
        self.grid_results.CreateGrid(0, 11)
        self.grid_results.SetColLabelValue(0, 'Date')
        self.grid_results.SetColLabelValue(1, 'Squawk')
        self.grid_results.SetColLabelValue(2, 'Callsign')
        self.grid_results.SetColLabelValue(3, 'Alert')
        self.grid_results.SetColLabelValue(4, 'Emergency')
        self.grid_results.SetColLabelValue(5, 'SPI')
        self.grid_results.SetColLabelValue(6, 'ModeS')
        self.grid_results.SetColLabelValue(7, 'Registration')
        self.grid_results.SetColLabelValue(8, 'Type')
        self.grid_results.SetColLabelValue(9, 'Operator')
        self.grid_results.SetColLabelValue(10, 'Country')
        self.grid_results.AutoSizeColumns()
        self.grid_results.EnableEditing(False)
        self.grid_results.SetToolTip(wx.ToolTip('Click the blue links for details.'))
        # button widgets
        self.button_search = wx.Button(self, ID_BUTTON_SEARCH, 'Search')
        self.button_clear = wx.Button(self, ID_BUTTON_CLEAR, 'Clear')
        self.button_stop = wx.Button(self, ID_BUTTON_STOP, 'Stop')
        self.button_stop.Enable(False)
        # box sizers
        self.box_sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_root = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_1.Add(self.static_text_squawk, 1, wx.EXPAND)
        self.box_sizer_1.Add(self.text_ctrl_squawk, 3, wx.EXPAND)
        self.box_sizer_1.AddStretchSpacer()
        self.box_sizer_1.Add(self.static_text_modes, 1, wx.EXPAND)
        self.box_sizer_1.Add(self.text_ctrl_modes, 3, wx.EXPAND)
        self.box_sizer_2.Add(self.static_text_callsign, 1, wx.EXPAND)
        self.box_sizer_2.Add(self.text_ctrl_callsign, 3, wx.EXPAND)
        self.box_sizer_2.AddStretchSpacer()
        self.box_sizer_2.Add(self.static_text_registration, 1, wx.EXPAND)
        self.box_sizer_2.Add(self.text_ctrl_registration, 3, wx.EXPAND)
        self.box_sizer_3.Add(self.static_text_alert, 1, wx.EXPAND)
        self.box_sizer_3.Add(self.combo_box_alert,3, wx.EXPAND)
        self.box_sizer_3.AddStretchSpacer()
        self.box_sizer_3.Add(self.static_text_type, 1, wx.EXPAND)
        self.box_sizer_3.Add(self.combo_box_type, 3, wx.EXPAND)
        self.box_sizer_4.Add(self.static_text_emergency, 1, wx.EXPAND)
        self.box_sizer_4.Add(self.combo_box_emergency, 3, wx.EXPAND)
        self.box_sizer_4.AddStretchSpacer()
        self.box_sizer_4.Add(self.static_text_operator, 1, wx.EXPAND)
        self.box_sizer_4.Add(self.text_ctrl_operator, 3, wx.EXPAND)
        self.box_sizer_5.Add(self.static_text_spi, 1, wx.EXPAND)
        self.box_sizer_5.Add(self.combo_box_spi, 3, wx.EXPAND)
        self.box_sizer_5.AddStretchSpacer()
        self.box_sizer_5.Add(self.static_text_country, 1, wx.EXPAND)
        self.box_sizer_5.Add(self.combo_box_country, 3, wx.EXPAND)
        self.box_sizer_6.Add(self.grid_results, 1, wx.EXPAND)
        self.box_sizer_7.Add(self.button_search, 1, wx.EXPAND)
        self.box_sizer_7.Add(self.button_clear, 1, wx.EXPAND)
        self.box_sizer_7.Add(self.button_stop, 1, wx.EXPAND)
        self.box_sizer_root.Add(self.box_sizer_1, 0, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_2, 0, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_3, 0, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_4, 0, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_5, 0, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_6, 1, wx.EXPAND | wx.ALL, 5)
        self.box_sizer_root.Add(self.box_sizer_7, 0, wx.EXPAND | wx.ALL, 5)
        # events
        wx.EVT_MENU(self, ID_MENU_FILE_OPEN, self.OnMenuFileOpen)
        wx.EVT_MENU(self, ID_MENU_FILE_EXIT, self.OnMenuFileExit)
        wx.EVT_MENU(self, ID_MENU_DATABASE_INFO, self.OnMenuDatabaseInfo)
        wx.EVT_MENU(self, ID_MENU_DATABASE_SEARCH, self.OnMenuDatabaseSearch)
        wx.EVT_MENU(self, ID_MENU_DATABASE_CLEAR, self.OnMenuDatabaseClear)
        wx.EVT_MENU(self, ID_MENU_HELP_HELP, self.OnMenuHelpHelp)
        wx.EVT_MENU(self, ID_MENU_HELP_ABOUT, self.OnMenuHelpAbout)
        wx.grid.EVT_GRID_CELL_LEFT_CLICK(self, self.OnGridResults)
        wx.EVT_BUTTON(self, ID_BUTTON_SEARCH, self.OnButtonSearch)
        wx.EVT_BUTTON(self, ID_BUTTON_CLEAR, self.OnButtonClear)
        wx.EVT_BUTTON(self, ID_BUTTON_STOP, self.OnButtonStop)
        EVT_RESULT(self, self.OnResult)
        # frame methods
        self.worker = None # set the worker attribute elsewhere
        self.CreateStatusBar()
        self.SetMenuBar(self.menu_bar)
        self.SetSizer(self.box_sizer_root)
        self.SetAutoLayout(True)
        #self.box_sizer_root.Fit(self)
        self.SetBackgroundColour(wx.NullColour)
        self.Show(True)

    def OnMenuFileOpen(self, event):
        file_dialog_open = wx.FileDialog(self, 'Please choose a database file.', '', 'BaseStation.sqb', '*.sqb')
        if file_dialog_open.ShowModal() != wx.ID_CANCEL:
            self.database_path = file_dialog_open.GetPath()
            self.SetStatusText('Opened ' + self.database_path + '.')

    def OnMenuFileExit(self, event):
        self.Close(True)

    def OnMenuDatabaseInfo(self, event):
        pass

    def OnMenuDatabaseSearch(self, event):
        if self.grid_results.GetNumberRows() != 0:
            self.grid_results.DeleteRows(0, self.grid_results.GetNumberRows())
        data = {
            'firstsquawk':self.text_ctrl_squawk.GetValue(),
            'callsign':self.text_ctrl_callsign.GetValue(),
            'hadalert':self.combo_box_alert.GetValue(),
            'hademergency':self.combo_box_emergency.GetValue(),
            'hadspi':self.combo_box_spi.GetValue(),
            'modes':self.text_ctrl_modes.GetValue(),
            'registration':self.text_ctrl_registration.GetValue(),
            'icaotypecode':self.combo_box_type.GetValue(),
            'operatorflagcode':self.text_ctrl_operator.GetValue(),
            'modescountry':self.combo_box_country.GetValue()}
        if not self.worker:
            try:
                if self.database_path != '' and len([element for element in data.values() if element != '']) != 0:
                    self.SetStatusText('Searching...')
                    try:
                        self.worker = SearchThread(self, self.database_path, data)
                    except business.DatabaseError, e:
                        self.SetStatusText('')
                        message_dialog_error = wx.MessageDialog(self, e.message, 'Database error', wx.OK | wx.ICON_ERROR)
                        message_dialog_error.ShowModal()
                    self.worker = None
                else:
                    message_dialog_warning = wx.MessageDialog(self, 'Please be more specific.', 'Warning', wx.OK | wx.ICON_WARNING)
                    message_dialog_warning.ShowModal()
            except AttributeError:
                message_dialog_error = wx.MessageDialog(self, 'Please open a database file first.', 'Error', wx.OK | wx.ICON_ERROR)
                message_dialog_error.ShowModal()

    def OnMenuDatabaseClear(self, event):
        self.text_ctrl_squawk.SetValue('')
        self.text_ctrl_callsign.SetValue('')
        self.combo_box_alert.SetValue('')
        self.combo_box_emergency.SetValue('')
        self.combo_box_spi.SetValue('')
        self.text_ctrl_modes.SetValue('')
        self.text_ctrl_registration.SetValue('')
        self.combo_box_type.SetValue('')
        self.text_ctrl_operator.SetValue('')
        self.combo_box_country.SetValue('')

    def OnMenuHelpHelp(self, event):
        pass

    def OnMenuHelpAbout(self, event):
        message_dialog_about = wx.MessageDialog(self, PROGRAM_NAME + ' ' + PROGRAM_VERSION + '\n\n' + 'Copyright 2008 ' + PROGRAM_AUTHOR, 'About', wx.OK)
        message_dialog_about.ShowModal()

    def OnGridResults(self, event):
        if event.GetCol() == 2 or 7:
            data = {}
            if event.GetCol() == 2:
                data['callsign'] = self.grid_results.GetCellValue(event.GetRow(), event.GetCol())
            if event.GetCol() == 7:
                data['registration'] = self.grid_results.GetCellValue(event.GetRow(), event.GetCol())
            aircraft_controller = business.AircraftController(self.database_path)
            aircraft_controller.browser_lookup(data)

    def OnButtonSearch(self, event):
        self.OnMenuDatabaseSearch(event)

    def OnButtonClear(self, event):
        self.OnMenuDatabaseClear(event)

    def OnButtonStop(self, event):
        if self.worker:
            self.worker.abort()

    def OnResult(self, event):
        if event.data == None:
            self.SetStatusText('Stopped search.') 
        else:
            self.grid_results.AppendRows(len(event.data))
            for row, table_row in zip(event.data, range(len(event.data))):
                self.grid_results.SetCellValue(table_row, 0, str(row[0]))
                self.grid_results.SetCellValue(table_row, 1, str(row[1]))
                self.grid_results.SetCellValue(table_row, 2, str(row[2]))
                self.grid_results.SetCellValue(table_row, 3, str(row[3]))
                self.grid_results.SetCellValue(table_row, 4, str(row[4]))
                self.grid_results.SetCellValue(table_row, 5, str(row[5]))
                self.grid_results.SetCellValue(table_row, 6, str(row[6]))
                self.grid_results.SetCellValue(table_row, 7, str(row[7]))
                self.grid_results.SetCellValue(table_row, 8, str(row[8]))
                self.grid_results.SetCellValue(table_row, 9, str(row[9]))
                self.grid_results.SetCellValue(table_row, 10, str(row[10]))
                self.grid_results.SetCellTextColour(table_row, 2, wx.Colour(0, 0, 255))
                self.grid_results.SetCellTextColour(table_row, 7, wx.Colour(0, 0, 255))
            self.grid_results.AutoSizeColumns()
            self.SetStatusText(str(len(event.data)) + ' records.')
        self.worker = None


class App:

    def __init__(self, title, size=(800, 600)):
        self.py_simple_app = wx.PySimpleApp()
        self.main_window = MainWindow(None, -1, title, size)
        self.py_simple_app.MainLoop()


app = App(PROGRAM_NAME)
