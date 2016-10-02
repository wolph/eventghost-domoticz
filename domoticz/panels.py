from __future__ import print_function

import abc

import wx

import eg_base


class Panel(eg_base.Panel):
    if eg_base.TESTING:
        def __init__(self, executable=None, resizable=True, showLine=True):
            eg_base.Panel.__init__(
                self, None, wx.ID_ANY, '%s Test' % self.__class__.__name__,
                style=wx.DEFAULT_DIALOG_STYLE | wx.THICK_FRAME
                      | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL, size=(800, 600))

            self.main_sizer = wx.BoxSizer(wx.VERTICAL)

            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.main_sizer.Add(self.sizer, 1, wx.EXPAND | wx.ALL, 0)

            self.button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
            self.main_sizer.Add(self.button_sizer, 0,
                                wx.ALIGN_CENTER | wx.BOTTOM, 0)

            self.SetSizer(self.main_sizer)

        def Affirmed(self):
            self.resultCode = self.ShowModal()
            if self.resultCode == wx.ID_CANCEL:
                return

            return self.resultCode

        def SetResult(self, *args):
            import pprint
            print('Set results to:')
            pprint.pprint(args)


class Base(object):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config', {})
        self.widgets = dict()
        self.row = 0

    def add(self, key, widget, row=None, col=None, flag=wx.EXPAND | wx.ALL):
        if row is None:
            row = self.row
            self.row += 1

        if col is None:
            col = 0
            span = 1, 2
        else:
            span = 1, 1

        pos = row, col

        self.sizer.Add(widget, pos=pos, span=span, flag=flag)
        self.widgets[key] = widget
        return widget

    def add_label(self, label, key=None, size=(-1, -1)):
        key = key or label

        if eg_base.TESTING and size == (-1, -1):
            # TODO: make wx somehow automatically resize this widget with the
            # window
            size = 100, -1

        self.add(
            'label_%s' % key,
            wx.StaticText(self.panel, label=label, size=size),
            row=self.row,
            col=0,
        )

    def add_field(self, label, key=None, widget=wx.TextCtrl, size=(-1, -1),
                  **kwargs):
        key = key or label

        if eg_base.TESTING and size == (-1, -1):
            # TODO: make wx somehow automatically resize this widget with the
            # window
            size = 600, -1

        self.add_label(label, key)

        return self.add(
            key,
            widget(self.panel,
                   value=unicode(self.config.get(key, '')),
                   size=size,
                   **kwargs),
            col=1,
        )

    def Configure(self, config=None, *args):
        self.row = 0
        self.widgets = dict()
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.panel = Panel()
        self.panel.sizer.Add(self.sizer, 1, wx.EXPAND | wx.ALL, 5)

        if config:
            self.config.update(config)

        return self.panel, self.config


class Action(Base, eg_base.Action):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self):
        raise NotImplementedError()


class Plugin(Base, eg_base.Plugin):
    def __start__(self, *args, **kwargs):
        pass

    def __stop__(self):
        pass

    def __close__(self):
        pass

    if eg_base.TESTING:
        def AddAction(self, class_):
            instance = class_()
            instance.plugin = self
            instance.Configure(self.config)

