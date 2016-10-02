from __future__ import print_function

import abc

import requests
import wx

import eg_base
import panels
import widgets


if not eg_base.TESTING:
    eg_base.eg.RegisterPlugin(
        name='Domoticz',
        guid='{3417a9ba-cbc9-4869-9f4d-87aaa9f57ac2}',
        author='Rick van Hattem <wolph@wol.ph>',
        version='0.1',
        kind='external',
        canMultiLoad=True,
        description='Adds Domoticz devices to EventGhost',
    )


class DomoticzPlugin(panels.Plugin):
    name = 'Domoticz'

    def __init__(self, *args, **kwargs):
        panels.Plugin.__init__(self, *args, **kwargs)
        self.AddAction(DomoticzRaw)
        self.AddAction(DomoticzSwitch)
        self.AddAction(DomoticzBlinds)
        self.AddAction(DomoticzDimmer)

    def __start__(self, config=None):
        panels.Plugin.__start__(self, config)
        if config:
            self.config.update(config)

    @property
    def url(self):
        url = self.config['host'].rstrip('/') + '/json.htm'
        if not url.startswith('http'):
            url = 'http://' + url
        return url

    def Configure(self, config=None, *args):
        panel, config = panels.Plugin.Configure(self, config, *args)
        config.setdefault('timeout', 3)

        self.add_field('host')
        self.add_field('user')
        self.add_field('pass', style=wx.TE_PASSWORD)
        self.add_field('timeout', widget=wx.SpinCtrlDouble)

        while panel.Affirmed():
            for k, v in self.widgets.items():
                if isinstance(v, wx.TextCtrl):
                    config[k] = v.GetValue().strip()

            try:
                self.getswitches()
                panel.SetResult(config)
                print('Successfully connected to %r' % self.url)
            except Exception as e:
                panels.print_error('Unable to connect: %r' % e)

    def execute(self, verbose=False, **params):
        config = self.config

        if config.get('user'):
            auth = config.get('user', ''), config.get('pass', '')
        else:
            auth = None

        if verbose:
            print(self.url, params)

        response = requests.get(self.url, auth=auth, params=params,
                                timeout=config.get('timeout', 3))
        data = response.json()
        assert data['status'] == 'OK'
        return data

    def getswitches(self, **kwargs):
        data = self.execute(
            type='devices',
            filter='light',
            used='true',
            **kwargs)['result']

        return dict((x['idx'], x) for x in data)


class DomoticzDevice(panels.Action):
    description = 'Sets a domoticz device to a given state'
    columns = (
        ('IDX', 'idx'),
        ('Name', ''),
        ('Status', ''),
        ('Last update', 'LastUpdate'),
    )

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError()

    def __call__(self, config, switchcmd, **kwargs):
        self.plugin.execute(
            type='command',
            param='switchlight',
            idx=config['idx'],
            switchcmd=switchcmd,
            verbose=True,
            **kwargs)

    def getswitches(self):
        data = dict()
        switch_type = getattr(self, 'switch_type', self.name)
        for key, value in self.plugin.getswitches().items():
            if value['SwitchType'] == switch_type or not switch_type:
                data[int(key)] = value
        return data

    def Configure(self, config=None, *args):
        panel, config = panels.Action.Configure(self, config, *args)

        switches = self.getswitches()

        if eg_base.TESTING:
            # TODO: make wx somehow automatically resize this widget with the
            # window
            size = 800, 500
        else:
            size = 500, -1

        switch_list = widgets.ListCtrl(
            panel, self.columns, switches, selected=config.get('idx'),
            style=wx.LC_SINGLE_SEL, size=size)

        self.add('switch', switch_list)

        return panel, config, switches, switch_list

    def affirm(self, panel, switches, switch_list):
        config = self.config
        while panel.Affirmed():
            value = self.widgets['value'].GetValue()
            selected = switch_list.GetFocusedItem()
            if selected != -1 and value is not None and value != '':
                idx = switch_list.GetItemData(selected)

                config['idx'] = idx
                config['value'] = value
                panel.SetResult(config)


class DomoticzRaw(DomoticzDevice):
    name = 'Raw'
    switch_type = None
    columns = DomoticzDevice.columns + (
        ('Type', 'SwitchType'),
    )

    def __call__(self, config):
        DomoticzDevice.__call__(
            self,
            config,
            switchcmd=config['value'],
        )

    def Configure(self, config=None, *args):
        panel, config, switches, switch_grid = DomoticzDevice.Configure(
            self, config, *args)
        self.add_field('value')
        self.affirm(panel, switches, switch_grid)


class DomoticzSwitch(DomoticzDevice):
    name = 'On/Off'

    def __call__(self, config):
        DomoticzDevice.__call__(
            self,
            config,
            switchcmd=config['value'],
        )

    def Configure(self, config=None, *args):
        panel, config, switches, switch_grid = DomoticzDevice.Configure(
            self, config, *args)
        self.add_field('value', widget=wx.ComboBox,
                       choices=('On', 'Off', 'Toggle'))
        self.affirm(panel, switches, switch_grid)


class DomoticzBlinds(DomoticzSwitch):
    name = 'Blinds'
    switch_type = 'Blinds Percentage'

    def __call__(self, config):
        DomoticzDevice.__call__(
            self,
            config,
            switchcmd='Set Level',
            level=config['value'],
        )

    def Configure(self, config=None, *args):
        panel, config, switches, switch_grid = DomoticzDevice.Configure(
            self, config, *args)
        self.add_field('value', widget=wx.ComboBox, choices=('Open', 'Close'))
        self.affirm(panel, switches, switch_grid)


class DomoticzDimmer(DomoticzDevice):
    name = 'Dimmer'

    def __call__(self, config):
        DomoticzDevice.__call__(
            self,
            config,
            switchcmd='Set Level',
            level=config['value'],
        )

    def Configure(self, config=None, *args):
        panel, config, switches, switch_grid = DomoticzDevice.Configure(
            self, config, *args)
        self.add_field('value', widget=wx.SpinCtrl)
        self.affirm(panel, switches, switch_grid)


if __name__ == '__main__':
    app = wx.App()
    plugin = DomoticzPlugin(config=dict(host='http://domoticz'))
    plugin.Configure()
