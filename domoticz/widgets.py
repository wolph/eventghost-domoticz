import wx
from wx.lib.mixins import listctrl

import eg_base


class ListCtrl(wx.ListCtrl, listctrl.ColumnSorterMixin):
    def __init__(self, parent, columns, data, selected=None, size=(-1, -1),
                 *args, **kwargs):
        self.columns = []
        self.rows = 0

        kwargs['style'] = kwargs.get('style', 0) | wx.LC_REPORT \
                          | wx.BORDER_SUNKEN

        wx.ListCtrl.__init__(self, parent, size=size, *args, **kwargs)
        listctrl.ColumnSorterMixin.__init__(self, len(columns))

        self.SetColumns(columns)
        self.setData(data, selected)

    def GetListCtrl(self):
        return self

    def SetColumns(self, columns):
        for i, (column, key) in enumerate(columns):
            key = key or column
            self.columns.append((column, key))
            self.InsertColumn(i, column)

        self.SetColumnCount(len(columns))

        listctrl.ColumnSorterMixin.__init__(self, len(columns))

    def AppendRow(self, values, selected=None):
        for i, (column, key) in enumerate(self.columns):
            if i:
                self.SetStringItem(self.rows, i, values[key])
            else:
                data = int(values[key])
                self.InsertStringItem(self.rows, values[key])
                self.SetItemData(self.rows, data)

                if selected == data:
                    self.Select(self.rows)

        self.rows += 1

    def setData(self, data, selected=None):
        self.itemDataMap = dict()
        for idx, values in data.items():
            idx = int(idx)
            self.itemDataMap[idx] = row = []
            for column, key in self.columns:
                if key == 'idx':
                    row.append(-idx)
                else:
                    row.append(values[key])

            self.AppendRow(values, selected)
